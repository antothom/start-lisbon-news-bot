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
        self.country_flags = {
            'Portugal': '🇵🇹',
            'Spain': '🇪🇸',
            'France': '🇫🇷',
            'Germany': '🇩🇪',
            'United Kingdom': '🇬🇧',
            'UK': '🇬🇧',
            'USA': '🇺🇸',
            'United States': '🇺🇸',
            'Netherlands': '🇳🇱',
            'Italy': '🇮🇹',
            'Switzerland': '🇨🇭',
            'Austria': '🇦🇹',
            'Belgium': '🇧🇪',
            'Sweden': '🇸🇪',
            'Czech Republic': '🇨🇿',
            'Norway': '🇳🇴',
            'Ireland': '🇮🇪',
            'Denmark': '🇩🇰',
            'Finland': '🇫🇮',
            'Estonia': '🇪🇪',
            'Poland': '🇵🇱',
            'Lithuania': '🇱🇹',
            'Latvia': '🇱🇻',
            'Romania': '🇷🇴',
        }
        self.news_category_emojis = {
            'Funding': '💰',
            'Acquisitions': '🤝',
            'Expansion': '🚀',
            'General News': '📰'
        }

    def add_news(self, title, summary, link, source, published, company, company_country, company_city, category):
        print("------------------------")
        print("AirtableManager - add_news: ", f"{title} - {summary[0:10]}... - Source: {source}")
        self.news_table.create({
            'Title': title,
            'Summary': summary,
            'Link': link,
            'Source': source,
            'Published': published,
            'Company': company,
            'Company_Country': self.get_country_with_flag(company_country),
            'Company_City': company_city,
            'Category': self.get_category_with_emoji(category)
        })
        print("\033[92m" + "News added successfully!" + "\033[0m")

    def add_event(self, title, summary, link, start_date, end_date, source, published, country, city):
        print("------------------------")
        print("AirtableManager - add_event: ", f"{title} - {summary[0:10]}...\nSource: {source}")
        try:
            self.events_table.create({
                'Title': title,
                'Summary': summary,
                'Link': link,
                'Start Date': start_date,
                'End Date': end_date,
                'Source': source,
                'Published': published,
                'Country': self.get_country_with_flag(country),
                'City': city
            })
            print("\033[92m" + "Event added successfully!" + "\033[0m")
        except Exception as e:
            print("\033[91m" + f"Error adding event: {title} - {e}" + "\033[0m")

    def add_job(self, position, company, location, link, source, published):
        print("------------------------")
        try:
            print("AirtableManager - add_job: ", f"{position} - {company}...\nSource: {source}")
            self.jobs_table.create({
                'Position': position,
                'Company': company,
                'Location': location,
                'Link': link,
                'Source': source,
                'Published': published
            })
            print("\033[92m" + "Job added successfully!" + "\033[0m")
        except Exception as e:
            print("\033[91m" + f"Error: {position} | {company} - {e}" + "\033[0m")

    def add_resource(self, title, summary, link, source, published):
        print("------------------------")
        print("AirtableManager - add_resource: ", f"{title} - {summary[0:10]}...\nSource: {source}")
        try:
            self.resources_table.create({
                'Title': title,
                'Summary': summary,
                'Link': link,
                'Source': source,
                'Published': published
            })
            print("\033[92m" + "Resource added successfully!" + "\033[0m")
        except Exception as e:
            print("\033[91m" + f"Error adding resource: {title} - {e}" + "\033[0m")


    def get_country_with_flag(self, country):
        if not country:
            return ""

        country = country.strip()
        flag = self.country_flags.get(country, '🌍')
        return f"{flag} {country}"

    def get_category_with_emoji(self, category):
        if not category:
            return ""
        category = category.strip()
        emoji = self.news_category_emojis.get(category, '📰')
        return f"{emoji} {category}"
