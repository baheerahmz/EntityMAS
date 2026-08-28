import os
from dotenv import load_dotenv


# Load settings from the .env file.
# override=True ensures the local project settings
# replace any older Windows environment variables.
load_dotenv(override=True)


# ==========================================
# LOCAL LLM CONFIGURATION
# ==========================================

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "qwen/qwen3-4b-2507"
)

BASE_URL = os.getenv(
    "BASE_URL",
    "http://127.0.0.1:1234/v1"
)


# ==========================================
# ROBUSTNESS CONFIGURATION
# ==========================================

TIMEOUT_SECONDS = 30

MAX_RETRIES = 3


# False = use the real local LLM through LM Studio
# True  = use our hard-coded mock responses
MOCK_MODE = False