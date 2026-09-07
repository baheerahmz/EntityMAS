import os #import the operating system module
from dotenv import load_dotenv #import the dotenv function


#Load settings from the .env file.
#override=True ensures the local project settings
#replace any older Windows environment variables.
load_dotenv(override=True) #load settings from the .env file


#==========================================
#LOCAL LLM CONFIGURATION
#==========================================

MODEL_NAME = os.getenv( #get the model name from environment settings
    "MODEL_NAME", #look for MODEL_NAME
    "qwen/qwen3-4b-2507" #use this model if no setting is found
)

BASE_URL = os.getenv( #get the LLM server URL
    "BASE_URL", #look for BASE_URL
    "http://127.0.0.1:1234/v1" #use the local LM Studio URL
)


#==========================================
#ROBUSTNESS CONFIGURATION
#==========================================

TIMEOUT_SECONDS = 30 #set the maximum waiting time

MAX_RETRIES = 3 #set the maximum number of retry attempts


#False = use the real local LLM through LM Studio
#True  = use our hard-coded mock responses
MOCK_MODE = False #use the real local LLM