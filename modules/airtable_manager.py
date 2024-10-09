import os
from dotenv import dotenv_values
from pyairtable import Api


class AirtableManager:
    def __init__(self):
        self.config = dotenv_values('.env')
        self.api = Api(self.config.get('AIRTABLE_ACCESS_TOKEN'))
        self.news_table = self.api.table('appKbQuX1KuPkXDTP', 'tbln8OD73miRY4c0z')
        self.events_table = self.api.table('appKbQuX1KuPkXDTP', 'tblWxehv7NNWtxKFP')
        self.jobs_table = self.api.table('appKbQuX1KuPkXDTP', 'tblWFHSJ5JMmPkbO7')
        self.resources_table = self.api.table('appKbQuX1KuPkXDTP', 'tbluJLuniJ0FrYjNu')

    def add_news(self, title, summary, link, source):
        self.news_table.create({
            'Title': title,
            'Summary': summary,
            'Link': link,
            'Source': source
        })

    def add_event(self, title, summary, link, date, source):
        self.events_table.create({
            'Title': title,
            'Summary': summary,
            'Link': link,
            'Date': date,
            'Source': source
        })

    def add_job(self, title, summary, link, source):
        self.jobs_table.create({
            'Title': title,
            'Summary': summary,
            'Link': link,
            'Source': source
        })

    def add_resource(self, title, summary, link, source):
        self.resources_table.create({
            'Title': title,
            'Summary': summary,
            'Link': link,
            'Source': source
        })
