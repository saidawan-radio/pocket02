import os
from dotenv import load_dotenv

load_dotenv()

class conf:
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", 0)
    SESSION_STR= os.getenv("SESSION_STR", 0)
    CHANNEL_USERNAME= os.getenv("CHANNEL_USERNAME", 0)
    DOWNLOAD_PATH=os.getenv("DOWNLOAD_PATH", 0)
    ORIGIN_DATA_FILE_PATH = os.getenv("ORIGIN_DATA_FILE_PATH", 0)
    DOWNLOADED_DATA_FILE_PATH = os.getenv("DOWNLOADED_DATA_FILE_PATH", 0)
    DATE_FORMAT = os.getenv("DATE_FORMAT", 0)
    LOAD_START_DATE = os.getenv("LOAD_START_DATE", 0)
    DURATION_LIMIT = int(os.getenv("DURATION_LIMIT", 0))
    MIN_MSG_ID = int(os.getenv("MIN_MSG_ID", 0))
    DATA_FETCH_LIMIT = int(os.getenv("DATA_FETCH_LIMIT", 0))
    DATA_FETCH_SIZE_LIMIT = os.getenv("DATA_FETCH_SIZE_LIMIT", 0)
    FILENAME_PATTERN = os.getenv("FILENAME_PATTERN", 0)
    COVER_PATH_DIR=os.getenv("COVER_PATH_DIR", 0)
    DOWNLOADED_JSON_DATA_FORM = {
                "audio_info" : {},
                "map_msg_id" : {},
                "general_info": {
                    "last_downloaded_internal_id": 0
                }
            }
    
    REPO_OWNER = os.getenv("REPO_OWNER", 0)
    REPO_NAME = os.getenv("REPO_NAME", 0)
    REPO_BRANCH = os.getenv("REPO_BRANCH", 0)
