from utils import utils
import pandas as pd
import feedparser
import requests



def fetch_rss_feed(rss_url: str, source_name: str):
    """
    Fetches and formats newsletters from an RSS feed URL.

    Params:
        rss_url (str): The URL of the RSS feed to fetch.
        source_name (str): The name of the source to tag the entries with.

    Returns:
        pd.DataFrame: A DataFrame containing the formatted newsletter entries with columns:
                      'published', 'source', 'title', 'content', and 'link'.
    """

    # Use the custom session to fetch the feed
    response = requests.get(rss_url)

    # Parse the feed content
    feed = feedparser.parse(response.content)

    formatted_feed = list()

    # Loop through each entry (article/item) in the feed
    for entry in feed.entries:
        # Format the entry and append it to the formatted_feed list
        formatted_entry = utils.format_rss_entry(entry)
        formatted_feed.append(formatted_entry)

    # Convert the list of formatted entries into a DataFrame
    formatted_feed = pd.DataFrame(formatted_feed)

    # Add the source name to the DataFrame
    formatted_feed['source'] = source_name

    # Reorder the columns
    formatted_feed = formatted_feed[['published', 'source', 'title', 'content', 'link']]

    return formatted_feed
