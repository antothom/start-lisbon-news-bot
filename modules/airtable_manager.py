import os
from dotenv import dotenv_values
from pyairtable import Api
import logging


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
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _prepare_social_images(self, images):
        """Helper method to prepare social image data for Airtable"""
        if not images:
            return None

        image_data = {}
        if isinstance(images, dict):
            # Handle multiple image types (og, twitter, etc)
            for img_type, img_path in images.items():
                if img_path and os.path.exists(img_path):
                    image_data[f'social_image_{img_type}'] = {'url': img_path}
        elif isinstance(images, str) and os.path.exists(images):
            # Handle single image path
            image_data['social_image'] = {'url': images}

        return image_data

    def add_news(self, title, summary, link, source, published, company, company_country, company_city, category,
                 social_images=None):
        print("------------------------")
        print("AirtableManager - add_news: ", f"{title} - {summary[0:10]}... - Source: {source}")

        try:
            record_data = {
                'Title': title,
                'Summary': summary,
                'Link': link,
                'Source': source,
                'Published': published,
                'Company': company,
                'Company_Country': self.get_country_with_flag(company_country),
                'Company_Country_flag': self.get_only_country_flag(company_country),
                'Company_City': company_city,
                'Category': self.get_category_with_emoji(category),
                'Image_Links': social_images if isinstance(social_images, str) else str(
                    social_images) if social_images else None
            }

            self.news_table.create(record_data)
            print("\033[92m" + "News added successfully!" + "\033[0m")
        except Exception as e:
            self.logger.error(f"Error adding news: {title} - {str(e)}")
            print("\033[91m" + f"Error adding news: {str(e)}" + "\033[0m")

    def add_event(self, title, summary, link, start_date, end_date, source, published, country, city,
                  social_images=None):
        print("------------------------")
        print("AirtableManager - add_event: ", f"{title} - {summary[0:10]}...\nSource: {source}")
        try:
            record_data = {
                'Title': title,
                'Summary': summary,
                'Link': link,
                'Start Date': start_date,
                'End Date': end_date,
                'Source': source,
                'Published': published,
                'Country': self.get_country_with_flag(country),
                'Country_flag': self.get_only_country_flag(country),
                'City': city,
                'Image_Links': social_images if isinstance(social_images, str) else str(
                    social_images) if social_images else None
            }

            self.events_table.create(record_data)
            print("\033[92m" + "Event added successfully!" + "\033[0m")
        except Exception as e:
            self.logger.error(f"Error adding event: {title} - {str(e)}")
            print("\033[91m" + f"Error adding event: {title} - {e}" + "\033[0m")

    def add_job(self, position, company, location, link, source, published, social_images=None):
        print("------------------------")
        try:
            print("AirtableManager - add_job: ", f"{position} - {company}...\nSource: {source}")

            record_data = {
                'Position': position,
                'Company': company,
                'Location': location,
                'Link': link,
                'Source': source,
                'Published': published,
                'Image_Links': social_images if isinstance(social_images, str) else str(
                    social_images) if social_images else None
            }

            self.jobs_table.create(record_data)
            print("\033[92m" + "Job added successfully!" + "\033[0m")
        except Exception as e:
            self.logger.error(f"Error adding job: {position} | {company} - {str(e)}")
            print("\033[91m" + f"Error: {position} | {company} - {e}" + "\033[0m")

    def get_country_with_flag(self, country):
        if not country:
            return ""

        country = country.strip()
        flag = self.country_flags.get(country, '🌍')
        return f"{flag} {country}"

    def get_only_country_flag(self, country):
        if not country:
            return ""

        flag = self.country_flags.get(country, '🌍')
        return f"{flag}"

    def get_category_with_emoji(self, category):
        if not category:
            return ""
        category = category.strip()
        emoji = self.news_category_emojis.get(category, '📰')
        return f"{emoji} {category}"
