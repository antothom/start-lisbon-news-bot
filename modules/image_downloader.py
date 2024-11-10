import os
import requests
from urllib.parse import urlparse
from pathlib import Path
import hashlib


class ImageDownloader:
    def __init__(self, base_path="scraped_images"):
        """Initialize with base path for saving images"""
        self.base_path = base_path
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        for dir_name in ['og_images', 'twitter_images', 'fallback_images']:
            Path(f"{self.base_path}/{dir_name}").mkdir(parents=True, exist_ok=True)

    def _get_file_extension(self, url, content_type=None):
        """Extract file extension from URL or content-type"""
        if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return os.path.splitext(url)[1]

        if content_type:
            extensions = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'image/webp': '.webp'
            }
            return extensions.get(content_type.lower(), '.jpg')

        return '.jpg'

    def _generate_filename(self, url, image_type):
        """Generate a unique filename based on URL and image type"""
        # Create hash from URL to ensure unique filename
        url_hash = hashlib.md5(url.encode()).hexdigest()[:10]

        # Get the original filename from URL
        parsed_url = urlparse(url)
        original_name = os.path.basename(parsed_url.path)

        # If original name is empty or just a hash/id, use the url_hash
        if not original_name or len(original_name) < 5:
            original_name = url_hash

        return f"{url_hash}_{original_name}"

    def download_image(self, url, image_type):
        """
        Download image from URL and save it to appropriate directory
        Returns tuple of (success, filepath or error message)
        """
        if not url:
            return False, "No URL provided"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Get content type and file extension
            content_type = response.headers.get('content-type')
            ext = self._get_file_extension(url, content_type)

            # Generate filename and path
            filename = self._generate_filename(url, image_type)
            if not filename.endswith(ext):
                filename += ext

            filepath = os.path.join(self.base_path, f"{image_type}_images", filename)

            # Save the image
            with open(filepath, 'wb') as f:
                f.write(response.content)

            return True, filepath

        except Exception as e:
            return False, f"Error downloading {url}: {str(e)}"

    def download_social_images(self, social_images):
        """
        Download all social images for a given set
        Returns dict with results
        """
        results = {
            'og_image': None,
            'twitter_image': None,
            'fallback_image': None
        }

        if not social_images:
            return results

        for image_type, url in social_images.items():
            if url:
                success, result = self.download_image(url, image_type.split('_')[0])
                results[image_type] = result if success else None

        return results