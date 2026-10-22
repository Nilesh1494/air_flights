import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import API_KEY, API_HOST

BASE_URL = f"https://{API_HOST}"

SESSION = requests.Session()
SESSION.mount(
    "https://",
    HTTPAdapter(
        max_retries=Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
    ),
)


def request_json(path, params=None, timeout=60):
    if not API_KEY:
        raise RuntimeError("RAPIDAPI_KEY is missing. Put it in .env")

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }

    response = SESSION.get(
        f"{BASE_URL}{path}",
        headers=headers,
        params=params,
        timeout=timeout,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"API error {response.status_code}: {response.text[:1000]}"
        )

    return response.json()
