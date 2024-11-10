import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging


class SocialImageScraper:
    """Helper class to extract social media preview images from URLs"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def extract_social_image(self, url):
        """
        Extracts social media preview images from a URL
        Returns a dict with different types of social media images found
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            images = {
                'og_image': None,
                'twitter_image': None,
                'fallback_image': None
            }

            # Try Open Graph image first
            og_image = soup.find('meta', property='og:image')
            if og_image:
                images['og_image'] = urljoin(url, og_image.get('content', ''))

            # Try Twitter image
            twitter_image = soup.find('meta', property='twitter:image')
            if twitter_image:
                images['twitter_image'] = urljoin(url, twitter_image.get('content', ''))

            # Fallback to first significant image
            if not images['og_image'] and not images['twitter_image']:
                main_image = soup.find('img', {'width': lambda x: x and int(x) >= 200})
                if main_image:
                    images['fallback_image'] = urljoin(url, main_image.get('src', ''))

            return images

        except Exception as e:
            logging.error(f"Error extracting social image from {url}: {str(e)}")
            return None