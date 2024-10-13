import requests
import json
from datetime import datetime
import pandas as pd


class APIFetcher:
    def __init__(self, source_url: str, source_name: str, date_threshold: datetime = None):
        self.api_url = source_url
        self.source_name = source_name
        self.date_threshold = date_threshold

    def fetch(self):
        """
        Fetches and formats newsletters from an API URL.

        Params:
            api_url (str): The URL of the API to fetch.
            source_name (str): The name of the source to tag the entries with.

        Returns:
            pd.DataFrame: A DataFrame containing the formatted newsletter entries with columns:
                          'published', 'source', 'title', 'content', and 'link'.
        """

        api_url = self.api_url
        source_name = self.source_name

        response = requests.get(api_url)
        data = response.json()

        entries = list()
        for entry in data:
            entries.append({
                'published': datetime.strptime(entry['publicationDate'], '%Y-%m-%d %H:%M:%S'),
                'source': source_name,
                'title': entry['title'],
                'content': entry['emailTemplate'],
                'link': "https://read.letterhead.email/techstars-portugal/" + entry['uniqueId']
            })

        df = pd.DataFrame(entries)

        return df
