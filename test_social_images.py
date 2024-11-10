import asyncio
import pandas as pd
from datetime import date, timedelta
from modules.rss_fetcher import RSSFetcher
from modules.api_fetcher import APIFetcher
from modules.data_extractor import DataExtractor
from modules.social_image_scraper import SocialImageScraper
from modules.image_downloader import ImageDownloader
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import os


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


async def test_process_dataframes(all_dfs):
    """Process all dataframes and print results to terminal"""
    console = Console()
    image_scraper = SocialImageScraper()
    image_downloader = ImageDownloader()

    for df_type, df in all_dfs.items():
        if df.empty:
            continue

        # Clean links
        df['Link'] = df['Link'].replace('', pd.NA)
        df = df.dropna(subset=['Link'])

        if len(df) == 0:
            continue

        console.print(f"\n[bold magenta]Processing {df_type}[/bold magenta]")

        # Fetch all social images for this dataframe asynchronously
        rprint(f"[yellow]Fetching social images for {len(df)} links...[/yellow]")
        social_images = await fetch_social_images(df['Link'].tolist(), image_scraper)

        # Download images
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

        # Create and populate table for this dataframe
        table = Table(show_header=True, header_style="bold blue")

        # Add columns based on dataframe type
        if df_type == 'News':
            table.add_column("Title", width=30)
            table.add_column("Company", width=20)
            table.add_column("Category", width=15)
            table.add_column("Social Images Found", width=40)

            for idx in df.index:
                images = social_images.get(df.loc[idx, 'Link'])
                image_info = []
                if images:
                    if images.get('og_image'): image_info.append("✓ OG Image")
                    if images.get('twitter_image'): image_info.append("✓ Twitter Image")
                    if images.get('fallback_image'): image_info.append("✓ Fallback Image")
                image_status = "\n".join(image_info) if image_info else "❌ No images found"

                table.add_row(
                    str(df.loc[idx, 'Title']),
                    str(df.loc[idx, 'Company']),
                    str(df.loc[idx, 'Category']),
                    image_status
                )

        elif df_type == 'Events':
            table.add_column("Title", width=30)
            table.add_column("Date", width=20)
            table.add_column("Location", width=20)
            table.add_column("Social Images Found", width=40)

            for idx in df.index:
                images = social_images.get(df.loc[idx, 'Link'])
                image_info = []
                if images:
                    if images.get('og_image'): image_info.append("✓ OG Image")
                    if images.get('twitter_image'): image_info.append("✓ Twitter Image")
                    if images.get('fallback_image'): image_info.append("✓ Fallback Image")
                image_status = "\n".join(image_info) if image_info else "❌ No images found"

                date_str = f"{df.loc[idx, 'Start Date']} - {df.loc[idx, 'End Date']}" if pd.notna(
                    df.loc[idx, 'End Date']) else str(df.loc[idx, 'Start Date'])
                location = f"{df.loc[idx, 'City']}, {df.loc[idx, 'Country']}" if pd.notna(df.loc[idx, 'City']) else str(
                    df.loc[idx, 'Country'])

                table.add_row(
                    str(df.loc[idx, 'Title']),
                    date_str,
                    location,
                    image_status
                )

        elif df_type == 'Jobs':
            table.add_column("Position", width=30)
            table.add_column("Company", width=20)
            table.add_column("Location", width=20)
            table.add_column("Social Images Found", width=40)

            for idx in df.index:
                images = social_images.get(df.loc[idx, 'Link'])
                image_info = []
                if images:
                    if images.get('og_image'): image_info.append("✓ OG Image")
                    if images.get('twitter_image'): image_info.append("✓ Twitter Image")
                    if images.get('fallback_image'): image_info.append("✓ Fallback Image")
                image_status = "\n".join(image_info) if image_info else "❌ No images found"

                table.add_row(
                    str(df.loc[idx, 'Position']),
                    str(df.loc[idx, 'Company']),
                    str(df.loc[idx, 'Location']),
                    image_status
                )

        # Print the table
        console.print(table)

        # Print detailed image URLs for debugging
        console.print("\n[bold green]Detailed Image URLs:[/bold green]")
        for link, images in social_images.items():
            if images:
                console.print(f"\n[bold]Link:[/bold] {link}")
                if images.get('og_image'):
                    console.print(f"[blue]OG Image:[/blue] {images['og_image']}")
                if images.get('twitter_image'):
                    console.print(f"[blue]Twitter Image:[/blue] {images['twitter_image']}")
                if images.get('fallback_image'):
                    console.print(f"[blue]Fallback Image:[/blue] {images['fallback_image']}")


async def main():
    # Read configuration
    feeds_df = pd.read_csv('config/newsletters.csv')

    feeds = {}
    for i in feeds_df.index:
        feeds[feeds_df.loc[i, 'name']] = (feeds_df.loc[i, 'feed'], feeds_df.loc[i, 'type'])

    # Fetch data from sources
    console = Console()
    for i in feeds:
        console.print(f"\n[bold cyan]Processing feed: {i}[/bold cyan]")

        if feeds[i][1] == 'RSS':
            fetcher = RSSFetcher(feeds[i][0], i, date.today() - timedelta(days=14))
        elif feeds[i][1] == 'API':
            fetcher = APIFetcher(feeds[i][0], i, date.today() - timedelta(days=14))

        fetched_data = fetcher.fetch()

        if fetched_data.empty:
            console.print(f"[yellow]WARNING: No new data for {i}[/yellow]")
            continue

        prompt_filename = "config/prompts/prompt_" + i.lower().replace(" ", "_") + ".txt"
        prompt = open(prompt_filename, "r").read()

        # Initialize DataFrames
        news_df = pd.DataFrame(
            columns=['Title', 'Summary', 'Link', 'Source', 'Published', 'Company', 'Company_Country', 'Company_City',
                     'Category'])
        events_df = pd.DataFrame(
            columns=['Title', 'Summary', 'Link', 'Start Date', 'End Date', 'Source', 'Published', 'Country', 'City'])
        jobs_df = pd.DataFrame(columns=['Position', 'Company', 'Location', 'Link', 'Source', 'Published'])
        resources_df = pd.DataFrame(columns=['Title', 'Summary', 'Link', 'Source', 'Published'])
        all_dfs = {'News': news_df, 'Events': events_df, 'Jobs': jobs_df, 'Resources': resources_df}

        # Extract data
        for j in fetched_data.index:
            extractor = DataExtractor(
                fetched_data.loc[j, 'content'],
                fetched_data.loc[j, 'published'],
                fetched_data.loc[j, 'source'],
                prompt
            )
            extracted = extractor.extract()
            curr_dfs = extractor.text_to_df(extracted)

            for k in curr_dfs:
                all_dfs[k] = pd.concat([all_dfs[k], curr_dfs[k]], ignore_index=True)

        # Process and display results
        await test_process_dataframes(all_dfs)


if __name__ == "__main__":
    asyncio.run(main())