"""
Klaviyo API client helper module.
"""
import os
from klaviyo_api import KlaviyoAPI

def get_klaviyo_client():
    """Get an initialized Klaviyo API client."""
    api_key = os.getenv("KLAVIYO_API_KEY")
    if not api_key:
        raise ValueError("KLAVIYO_API_KEY environment variable is not set")
    return KlaviyoAPI(api_key, max_delay=60, max_retries=3, test_host=None)
