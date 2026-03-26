import requests
from typing import Optional, Dict

# 🔥 GLOBAL USER AGENT (mentor requirement)
DEFAULT_HEADERS = {
    "User-Agent": "IndianCulturalDatasetBot/1.0 (Educational Project; contact: your_email@example.com)"
}


def safe_request(
    url: str,
    headers: Optional[Dict] = None,
    timeout: int = 10
):
    """
    Safe HTTP request with proper headers
    """

    try:
        # Merge headers (custom + default)
        final_headers = DEFAULT_HEADERS.copy()

        if headers:
            final_headers.update(headers)

        response = requests.get(
            url,
            headers=final_headers,
            timeout=timeout
        )

        if response.status_code == 200:
            return response.content

    except Exception:
        return None

    return None