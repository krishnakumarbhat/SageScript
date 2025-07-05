"""
api_client.py

A simple example of making HTTP requests using the requests library.
"""

import requests
from typing import Optional, Dict


class APIClient:
    """Client to interact with a REST API."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip('/')

    def get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Optional[Dict]:
        """
        Send a GET request to the API.

        Args:
            endpoint: API endpoint path.
            params: Query parameters.

        Returns:
            JSON response as a dictionary if successful, None otherwise.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            print(f"Request failed: {error}")
            return None


if __name__ == "__main__":
    client = APIClient("https://jsonplaceholder.typicode.com")
    posts = client.get("/posts", params={"userId": "1"})
    if posts:
        print(f"Received {len(posts)} posts for userId=1")
        print(posts[0])  # Print first post
