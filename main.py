import pandas as pd

from modules.rss_fetcher import RSSFetcher
from modules.api_fetcher import APIFetcher
from modules.data_extractor import DataExtractor
from modules.airtable_manager import AirtableManager
from datetime import date
from datetime import timedelta


def main():
    feeds_df = pd.read_csv('config/newsletters.csv')

    feeds = {}
    for i in feeds_df.index:
        feeds[feeds_df.loc[i, 'name']] = (feeds_df.loc[i, 'feed'], feeds_df.loc[i, 'type'])

    fetched_data = {}
    for i in feeds:
        if feeds[i][1] == 'RSS':
            fetcher = RSSFetcher(feeds[i][0], i, date.today() - timedelta(days=14))
        elif feeds[i][1] == 'API':
            fetcher = APIFetcher(feeds[i][0], i, date.today() - timedelta(days=14))
        fetched_data[i] = fetcher.fetch()

    airtable_manager = AirtableManager()

    for i in fetched_data:
        if fetched_data[i].empty:
            print(f"\033[93mWARNING: No new data for {i}\033[0m")
            continue
        prompt_filename = "config/prompts/prompt_" + i.lower().replace(" ", "_") + ".txt"
        prompt = open(prompt_filename, "r").read()

        news_df = pd.DataFrame(
            columns=['Title', 'Summary', 'Link', 'Source', 'Published', 'Company', 'Company_Country', 'Company_City'])
        events_df = pd.DataFrame(
            columns=['Title', 'Summary', 'Link', 'Start Date', 'End Date', 'Source', 'Published', 'Country', 'City'])
        jobs_df = pd.DataFrame(columns=['Position', 'Company', 'Location', 'Link', 'Source', 'Published'])
        resources_df = pd.DataFrame(columns=['Title', 'Summary', 'Link', 'Source', 'Published'])
        all_dfs = {'News': news_df, 'Events': events_df, 'Jobs': jobs_df, 'Resources': resources_df}

        for j in fetched_data[i].index:
            extractor = DataExtractor(fetched_data[i].loc[j, 'content'], fetched_data[i].loc[j, 'published'],
                                      fetched_data[i].loc[j, 'source'], prompt)
            extracted = extractor.extract()
            curr_dfs = extractor.text_to_df(extracted)
            for k in curr_dfs:
                all_dfs[k] = pd.concat([all_dfs[k], curr_dfs[k]], ignore_index=True)

        for i in all_dfs:
            for j in all_dfs[i].index:
                if i == 'News':
                    airtable_manager.add_news(all_dfs[i].loc[j, 'Title'],
                                              all_dfs[i].loc[j, 'Summary'],
                                              all_dfs[i].loc[j, 'Link'],
                                              all_dfs[i].loc[j, 'Source'],
                                              all_dfs[i].loc[j, 'Published'].strftime('%Y-%m-%d'),
                                              all_dfs[i].loc[j, 'Company'],
                                              all_dfs[i].loc[j, 'Company_Country'],
                                              all_dfs[i].loc[j, 'Company_City'])
                elif i == 'Events':
                    airtable_manager.add_event(all_dfs[i].loc[j, 'Title'],
                                               all_dfs[i].loc[j, 'Summary'],
                                               all_dfs[i].loc[j, 'Link'],
                                               all_dfs[i].loc[j, 'Start Date'],
                                               all_dfs[i].loc[j, 'End Date'],
                                               all_dfs[i].loc[j, 'Source'],
                                               all_dfs[i].loc[j, 'Published'].strftime('%Y-%m-%d'),
                                               all_dfs[i].loc[j, 'Country'],
                                               all_dfs[i].loc[j, 'City'])
                elif i == 'Jobs':
                    airtable_manager.add_job(all_dfs[i].loc[j, 'Position'],
                                             all_dfs[i].loc[j, 'Company'],
                                             all_dfs[i].loc[j, 'Location'],
                                             all_dfs[i].loc[j, 'Link'],
                                             all_dfs[i].loc[j, 'Source'],
                                             all_dfs[i].loc[j, 'Published'].strftime('%Y-%m-%d'))
                elif i == 'Resources':
                    airtable_manager.add_resource(all_dfs[i].loc[j, 'Title'],
                                                  all_dfs[i].loc[j, 'Summary'],
                                                  all_dfs[i].loc[j, 'Link'],
                                                  all_dfs[i].loc[j, 'Source'],
                                                  all_dfs[i].loc[j, 'Published'].strftime('%Y-%m-%d'))


if __name__ == "__main__":
    main()