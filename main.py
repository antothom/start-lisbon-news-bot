import pandas as pd

from modules.rss_fetcher import RSSFetcher
from modules.data_extractor import DataExtractor

def main():
    feeds = pd.read_csv('config/newsletters.csv')

    feeds = dict(zip(feeds['name'], feeds['feed']))

    feeds
    #openai_api_key = 'your_openai_api_key'
    #airtable_api_key = 'your_airtable_api_key'
    #airtable_base_id = 'your_airtable_base_id'
    #airtable_table_name = 'your_airtable_table_name'

    # Initialize classes
    fetcher = RSSFetcher(feeds['Startup Portugal'], 'Startup Portugal')

    raw_entries = fetcher.fetch()

    file = open("config/prompt.txt", "r")
    prompt = file.read()

    extractor = DataExtractor(raw_entries.loc[1, 'content'], raw_entries.loc[1, 'source'], prompt)

    extracted = extractor.extract()

    extracted



if __name__ == "__main__":
    main()
