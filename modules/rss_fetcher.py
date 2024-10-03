from utils import utils
import pandas as pd
import feedparser
import requests
import html2text
from datetime import datetime
from time import mktime

class RSSFetcher:
    def __init__(self, source_url: str, source_name: str):
        self.rss_url = source_url
        self.source_name = source_name

    def __format_rss_entry(self, entry: dict):
        """
        Formats an RSS feed entry into a dictionary with specific fields.
        Converts the HTML content into formatted text.

        Params:
            entry (dict): A dictionary representing an RSS feed entry.

        Returns:
            dict: A dictionary containing the formatted entry with keys:
                  'title', 'published', 'link', and 'content'.
        """

        entry_dict = dict()

        # Extract and store the title from the entry
        entry_dict['title'] = entry['title']

        # Convert the published time to a datetime object and store it
        entry_dict['published'] = datetime.fromtimestamp(mktime(entry['published_parsed']))

        # Extract and store the link from the entry
        entry_dict['link'] = entry['link']

        # Extract and store the content from the entry (assumes the first content block)
        entry_dict['content'] = entry['content'][0]['value']

        # Turn the HTML content into formatted text
        config = html2text.HTML2Text()
        entry_dict['content'] = config.handle(entry_dict['content'])

        return entry_dict

    def fetch(self):
        """
        Fetches and formats newsletters from an RSS feed URL.

        Params:
            rss_url (str): The URL of the RSS feed to fetch.
            source_name (str): The name of the source to tag the entries with.

        Returns:
            pd.DataFrame: A DataFrame containing the formatted newsletter entries with columns:
                          'published', 'source', 'title', 'content', and 'link'.
        """

        source_url = self.rss_url
        source_name = self.source_name

        # Use the custom session to fetch the feed
        response = requests.get(source_url)

        # Parse the feed content
        feed = feedparser.parse(response.content)

        formatted_feed = list()

        # Loop through each entry (article/item) in the feed
        for entry in feed.entries:
            # Format the entry and append it to the formatted_feed list
            formatted_entry = self.__format_rss_entry(entry)
            formatted_feed.append(formatted_entry)

        # Convert the list of formatted entries into a DataFrame
        formatted_feed = pd.DataFrame(formatted_feed)

        # Add the source name to the DataFrame
        formatted_feed['source'] = source_name

        # Reorder the columns
        formatted_feed = formatted_feed[['published', 'source', 'title', 'content', 'link']]

        return formatted_feed