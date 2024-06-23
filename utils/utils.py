from datetime import datetime
from time import mktime
import html2text


def format_rss_entry(entry: dict):
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
