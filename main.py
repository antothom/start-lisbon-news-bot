import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
from modules.rss_fetcher import RSSFetcher
from modules.api_fetcher import APIFetcher
from modules.data_extractor import DataExtractor
from modules.airtable_manager import AirtableManager
from modules.social_image_scraper import SocialImageScraper
from modules.image_downloader import ImageDownloader
from datetime import date, timedelta
import time
import numpy as np
from rich.console import Console


async def fetch_social_images(links, image_scraper):
    """Asynchronously fetch social images for multiple links"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        tasks = [
            loop.run_in_executor(pool, image_scraper.extract_social_image, link)
            for link in links if pd.notna(link)
        ]
        results = await asyncio.gather(*tasks)
        return dict(zip(links, results))


async def process_and_store_images(df_type, df, image_scraper, image_downloader, console):
    """Process images for a dataframe and store them"""
    if df.empty:
        return

    df['Link'] = df['Link'].replace('', np.nan)
    df = df.dropna(subset=['Link'])

    if len(df) == 0:
        return

    console.print(f"\n[bold magenta]Processing {df_type}[/bold magenta]")
    console.print(f"[yellow]Fetching social images for {len(df)} links...[/yellow]")

    social_images = await fetch_social_images(df['Link'].tolist(), image_scraper)

    console.print("\n[bold green]Downloading images...[/bold green]")
    for link, images in social_images.items():
        if images:
            console.print(f"\n[bold]Link:[/bold] {link}")
            download_results = image_downloader.download_social_images(images)

            for image_type, result in download_results.items():
                if result:
                    if isinstance(result, str) and os.path.exists(result):
                        console.print(f"[green]✓[/green] {image_type} saved to: {result}")
                    else:
                        console.print(f"[red]✗[/red] {image_type}: {result}")

    return social_images


async def process_dataframes(all_dfs, airtable_manager):
    """Process all dataframes and add entries to Airtable"""
    image_scraper = SocialImageScraper()
    image_downloader = ImageDownloader()
    console = Console()

    for df_type, df in all_dfs.items():
        if df.empty:
            continue

        social_images = await process_and_store_images(df_type, df, image_scraper, image_downloader, console)

        if not social_images:
            continue

        for idx in df.index:
            try:
                if df_type == 'News':
                    await asyncio.sleep(1)  # Rate limiting
                    airtable_manager.add_news(
                        df.loc[idx, 'Title'],
                        df.loc[idx, 'Summary'],
                        df.loc[idx, 'Link'],
                        df.loc[idx, 'Source'],
                        df.loc[idx, 'Published'].strftime('%Y-%m-%d'),
                        df.loc[idx, 'Company'],
                        df.loc[idx, 'Company_Country'],
                        df.loc[idx, 'Company_City'],
                        df.loc[idx, 'Category'],
                        social_images.get(df.loc[idx, 'Link'])
                    )

                elif df_type == 'Events':
                    await asyncio.sleep(1)
                    try:
                        start_date = pd.to_datetime(df.loc[idx, 'Start Date']).strftime('%Y-%m-%d') if pd.notna(
                            df.loc[idx, 'Start Date']) else None
                    except:
                        start_date = df.loc[idx, 'Published'].strftime('%Y-%m-%d')
                    try:
                        end_date = pd.to_datetime(df.loc[idx, 'End Date']).strftime('%Y-%m-%d') if pd.notna(
                            df.loc[idx, 'End Date']) else None
                    except:
                        end_date = None

                    airtable_manager.add_event(
                        df.loc[idx, 'Title'],
                        df.loc[idx, 'Summary'],
                        df.loc[idx, 'Link'],
                        start_date,
                        end_date,
                        df.loc[idx, 'Source'],
                        df.loc[idx, 'Published'].strftime('%Y-%m-%d'),
                        df.loc[idx, 'Country'],
                        df.loc[idx, 'City'],
                        social_images.get(df.loc[idx, 'Link'])
                    )

                elif df_type == 'Jobs':
                    await asyncio.sleep(1)
                    airtable_manager.add_job(
                        df.loc[idx, 'Position'],
                        df.loc[idx, 'Company'],
                        df.loc[idx, 'Location'],
                        df.loc[idx, 'Link'],
                        df.loc[idx, 'Source'],
                        df.loc[idx, 'Published'].strftime('%Y-%m-%d'),
                        social_images.get(df.loc[idx, 'Link'])
                    )

            except Exception as e:
                console.print(f"[red]Error processing {df_type} entry: {str(e)}[/red]")


async def main():
    console = Console()

    # Read configuration
    feeds_df = pd.read_csv('config/newsletters.csv')

    feeds = {}
    for i in feeds_df.index:
        feeds[feeds_df.loc[i, 'name']] = (feeds_df.loc[i, 'feed'], feeds_df.loc[i, 'type'])

    # Fetch data from sources
    fetched_data = {}
    for i in feeds:
        console.print(f"\n[bold cyan]Processing feed: {i}[/bold cyan]")

        if feeds[i][1] == 'RSS':
            fetcher = RSSFetcher(feeds[i][0], i, date.today() - timedelta(days=14))
        elif feeds[i][1] == 'API':
            fetcher = APIFetcher(feeds[i][0], i, date.today() - timedelta(days=14))
        fetched_data[i] = fetcher.fetch()

    airtable_manager = AirtableManager()

    for i in fetched_data:
        if fetched_data[i].empty:
            console.print(f"[yellow]WARNING: No new data for {i}[/yellow]")
            continue

        prompt_filename = "config/prompts/prompt_" + i.lower().replace(" ", "_") + ".txt"
        prompt = open(prompt_filename, "r").read()

        news_df = pd.DataFrame(
            columns=['Title', 'Summary', 'Link', 'Source', 'Published', 'Company', 'Company_Country', 'Company_City',
                     'Category'])
        events_df = pd.DataFrame(
            columns=['Title', 'Summary', 'Link', 'Start Date', 'End Date', 'Source', 'Published', 'Country', 'City'])
        jobs_df = pd.DataFrame(columns=['Position', 'Company', 'Location', 'Link', 'Source', 'Published'])
        resources_df = pd.DataFrame(columns=['Title', 'Summary', 'Link', 'Source', 'Published'])
        all_dfs = {'News': news_df, 'Events': events_df, 'Jobs': jobs_df, 'Resources': resources_df}

        for j in fetched_data[i].index:
            extractor = DataExtractor(
                fetched_data[i].loc[j, 'content'],
                fetched_data[i].loc[j, 'published'],
                fetched_data[i].loc[j, 'source'],
                prompt
            )
            extracted = extractor.extract()
            curr_dfs = extractor.text_to_df(extracted)

            for k in curr_dfs:
                all_dfs[k] = pd.concat([all_dfs[k], curr_dfs[k]], ignore_index=True)

        await process_dataframes(all_dfs, airtable_manager)


if __name__ == "__main__":
    asyncio.run(main())