import asyncio
from telethon import TelegramClient
from telethon.tl.types import Message
from telethon.sessions import StringSession
from AudioDetail import AudioDetail
from FetchDetail import load_json,dump_json, create_and_fill_if_empty
from DownloadAudio import download_audio_by_internal_id,add_opus_extension,add_github_raw_url_to_detail, add_cover_image_url_to_detail
from datetime import datetime
import json
from config import conf


API_ID = int(conf.API_ID)
API_HASH = conf.API_HASH
SESSION_OBJ=StringSession(conf.SESSION_STR)

CHANNEL_USERNAME = conf.CHANNEL_USERNAME
DOWNLOAD_PATH= conf.DOWNLOAD_PATH
DATE_FORMAT = conf.DATE_FORMAT
LOAD_START_DATE = conf.LOAD_START_DATE
DURATION_LIMIT = int(conf.DURATION_LIMIT)
MIN_MSG_ID = int(conf.MIN_MSG_ID)
# DATA_FETCH_LIMIT = int(conf.DATA_FETCH_LIMIT)
DATA_FETCH_SIZE_LIMIT = conf.DATA_FETCH_SIZE_LIMIT
FILENAME_PATTERN = conf.FILENAME_PATTERN



#-----------------------------------------------------
#---------------- Define Functions -------------------

origin_data = load_json(conf.ORIGIN_DATA_FILE_PATH)

create_and_fill_if_empty(conf.DOWNLOADED_DATA_FILE_PATH, conf.DOWNLOADED_JSON_DATA_FORM)

downloaded_data = load_json(conf.DOWNLOADED_DATA_FILE_PATH)

async def main():
    client = TelegramClient(SESSION_OBJ, API_ID, API_HASH)
    await client.start()
    channel = await client.get_input_entity(CHANNEL_USERNAME)
    last_downloaded_intid = int(downloaded_data["general_info"]["last_downloaded_internal_id"]) + 1
    if origin_data["audio_info"][str(last_downloaded_intid)]:
        origin_detail = origin_data["audio_info"][str(last_downloaded_intid)]
        await download_audio_by_internal_id(client, channel, origin_data, last_downloaded_intid, conf.DOWNLOAD_PATH )
        opus_filename = add_opus_extension(origin_detail["filename"])
        new_detail = add_github_raw_url_to_detail(origin_detail, conf.DOWNLOAD_PATH, opus_filename, conf.REPO_OWNER, conf.REPO_NAME, conf.REPO_BRANCH)
        new_detail = add_cover_image_url_to_detail(new_detail, conf.COVER_PATH_DIR, conf.REPO_OWNER, conf.REPO_NAME, conf.REPO_BRANCH)
        print(new_detail)
        downloaded_data["audio_info"][str(last_downloaded_intid)] = new_detail
        downloaded_data["general_info"]["last_downloaded_internal_id"] = last_downloaded_intid
    dump_json(conf.DOWNLOADED_DATA_FILE_PATH, downloaded_data)
    
        
    

asyncio.run(main())





