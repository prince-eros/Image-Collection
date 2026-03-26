import os
from dotenv import load_dotenv


# Load .env file
load_dotenv()


class Config:
    """
    Dynamic configuration loader.
    Automatically loads all API keys from .env
    """

    # Store all environment variables
    ENV = dict(os.environ)

    # =========================
    # GENERIC GETTER
    # =========================

    @staticmethod
    def get(key: str, default=None):
        return os.getenv(key, default)

    # =========================
    # API KEY GETTER
    # =========================

    @staticmethod
    def get_api_key(source_name: str) -> str:
        """
        Example:
        get_api_key("pexels") → PEXELS_API_KEY
        """

        key_name = f"{source_name.upper()}_API_KEY"
        value = os.getenv(key_name)

        if not value:
            raise ValueError(f"Missing API key: {key_name}")

        return value

    # =========================
    # OPTIONAL VALIDATION
    # =========================

    @staticmethod
    def validate(required_keys=None):
        """
        Validate required keys if needed
        """
        if not required_keys:
            return

        missing = []

        for key in required_keys:
            if not os.getenv(key):
                missing.append(key)

        if missing:
            raise ValueError(f"Missing API keys: {missing}")