import pandas as pd

from modules.rss_fetcher import RSSFetcher
from modules.data_extractor import DataExtractor
from modules.airtable_manager import AirtableManager


def main():
    feeds = pd.read_csv('config/newsletters.csv')

    feeds = dict(zip(feeds['name'], feeds['feed']))

    fetched_data = {}

    for i in feeds:
        fetcher = RSSFetcher(feeds[i], i)
        fetched_data[i] = fetcher.fetch()

    airtable_manager = AirtableManager()

    for i in fetched_data:
        if i == 'Startup Portugal':
            prompt = open("config/prompt.txt", "r").read()
            extractor = DataExtractor(fetched_data[i].loc[2, 'content'], fetched_data[i].loc[2, 'source'], prompt)
            extracted = extractor.extract()
            all_dfs = extractor.text_to_df(extracted)

            for i in all_dfs:
                for j in all_dfs[i].index:
                    if i == 'News':
                        airtable_manager.add_news(all_dfs[i].loc[j, 'Title'],
                                                  all_dfs[i].loc[j, 'Summary'],
                                                  all_dfs[i].loc[j, 'Link'],
                                                  all_dfs[i].loc[j, 'Source'])
                    elif i == 'Events':
                        airtable_manager.add_event(all_dfs[i].loc[j, 'Title'],
                                                   all_dfs[i].loc[j, 'Summary'],
                                                   all_dfs[i].loc[j, 'Link'],
                                                   all_dfs[i].loc[j, 'Date'],
                                                   all_dfs[i].loc[j, 'Source'])
                    elif i == 'Jobs':
                        airtable_manager.add_job(all_dfs[i].loc[j, 'Title'],
                                                all_dfs[i].loc[j, 'Summary'],
                                                all_dfs[i].loc[j, 'Link'],
                                                all_dfs[i].loc[j, 'Source'])
                    elif i == 'Resources':
                        airtable_manager.add_resource(all_dfs[i].loc[j, 'Title'],
                                                    all_dfs[i].loc[j, 'Summary'],
                                                    all_dfs[i].loc[j, 'Link'],
                                                    all_dfs[i].loc[j, 'Source'])


if __name__ == "__main__":
    main()
