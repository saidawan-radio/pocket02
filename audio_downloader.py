import os
import asyncio
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeAudio, Message
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import logging
from datetime import datetime
from dotenv import load_dotenv
import json
import re

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_OBJ=StringSession(os.getenv("SESSION_STR"))

CHANNEL_USERNAME=os.getenv("CHANNEL_USERNAME")
DOWNLOAD_PATH=os.getenv("DOWNLOAD_PATH")
DATA_FILE_PATH = os.getenv("DATA_FILE_PATH")
DATE_FORMAT = os.getenv("DATE_FORMAT")
LOAD_START_DATE = os.getenv("LOAD_START_DATE")
DURATION_LIMIT = int(os.getenv("DURATION_LIMIT"))
MIN_MSG_ID = int(os.getenv("MIN_MSG_ID"))
DATA_FETCH_LIMIT = int(os.getenv("DATA_FETCH_LIMIT"))
DATA_FETCH_SIZE_LIMIT = os.getenv("DATA_FETCH_SIZE_LIMIT")
FILENAME_PATTERN = os.getenv("FILENAME_PATTERN")

proxy=("http", "127.0.0.1", 10808)

extension_map = {
    'audio/mpeg': 'mp3',
    'audio/mp3': 'mp3',
    'audio/mp4': 'm4a',
    'audio/m4a': 'm4a',
    'audio/ogg': 'ogg',
    'audio/flac': 'flac',
    'audio/aac': 'aac',
    'audio/wav': 'wav',
    'audio/x-wav': 'wav',
    'audio/webm': 'webm',
    'audio/x-aac': 'acc'
}


#-----------------------------------------------------
#---------------- Define Functions -------------------

def load_json(file):
    with open(file, 'r', encoding="utf-8") as f:
        data = json.load(f)
        return data

def dump_json(file, data):
    with open(file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def load_datetime(strdate, strformat):
    return datetime.strptime(strdate, strformat)

def audio_detail_update(audio:AudioDetail, data:dict):
    stored_detail_id = data["map_msg_id"][audio.msg_id]
    stored_detail = data["audio_info"][stored_detail_id]
    if load_datetime(audio.edit_date, DATE_FORMAT) > load_datetime(stored_detail["edit_date"], DATE_FORMAT):
        data["audio_info"][stored_detail_id] = audio.to_dict()

def audio_detail_append(audio:AudioDetail, data:dict):
    if audio.msg_id in data["map_msg_id"]:
        audio.id = data["map_msg_id"][audio.msg_id]
        audio_detail_update(audio, data)
    else:
        data["general_info"]["last_internal_id"] += 1
        audio.id = data["general_info"]["last_internal_id"]
        data["audio_info"][audio.id] = audio.to_dict()
        data["map_msg_id"][audio.msg_id] = audio.id

#----------------------------------------------------------

data = {
    "audio_info" : {},
    "map_msg_id" : {},
    "general_info": {
        "last_internal_id": 0
    }
}

data = load_json(DATA_FILE_PATH)
        
async def get_msg_by_audio_detail(client:TelegramClient,chat, audio:AudioDetail):

    msg = await client.get_messages(chat, ids=int(audio.msg_id))
    return msg

async def downoad_audio_by_msg(msg:Message, file_path:str, file_name:str):
    if hasattr(msg, "audio") and msg.audio:
        file = f"{file_path}/{file_name}"
        await msg.download_media(file=file)

async def download_audio_by_audio_detail(client:TelegramClient, chat, audio:AudioDetail):
    msg = await get_msg_by_audio_detail(client, chat, audio)
    await downoad_audio_by_msg(msg, DOWNLAOD_PATH, audio.filename)




class AudioDetail:
    def __init__(self, msg, id=None):
        self._id = id
        self.attribute_audio = self.getDocumentAttributeAudio(msg)
        self.title = self.get_title(self.attribute_audio)
        self.performer = self.get_performer(self.attribute_audio)
        self.duration = self.get_duration(self.attribute_audio)
        self.date = self.get_date(msg)
        self.author_name = self.get_author(msg)
        self.channel = self.get_channel(msg)
        self.msg_id = self.get_msg_id(msg)
        self.message = self.get_msg_text(msg)
        self.edit_date = self.get_edit_date(msg)
        self.mime_type = self.get_mime_type(msg)
        self.extension = self.get_extension()
        self.size = self.get_size(msg)
        self.document_id = self.get_document_id(msg)
    
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, val):
        self._id = str(val)

    @property
    def filename(self):
        return self.generate_filename()

    def getDocumentAttributeAudio(self, msg):
        for atribute in msg.audio.attributes:
            if isinstance(atribute, DocumentAttributeAudio):
                return atribute

    def get_title(self, attribute_audio):
        return attribute_audio.title
    
    def get_performer(self, attribute_audio):
        return attribute_audio.performer
    
    def get_duration(self, attribute_audio):
        return attribute_audio.duration
    
    def get_date(self, msg):
        return msg.date.strftime("%Y%m%d-%H%M")
    
    def get_author(self, msg):
        return msg.post_author
    
    def get_channel(self, msg):
        return {
            "id" : msg.chat.id,
            "username" : msg.chat.username,
            "name" : msg.chat.title
        }

    def get_msg_id(self, msg):
        return str(msg.id)
    
    def get_msg_text(self, msg):
        return msg.message
    
    def get_mime_type(self, msg):
        if msg.audio:
            return msg.audio.mime_type
    
    def get_extension(self):
        mime = self.mime_type.lower()
        if mime in extension_map:
            return extension_map[mime]
        else:
            print(f"msg id: {self.msg_id}: extension not found: ", self.mime_type)
            return None
    
    def get_size(self, msg):
        # Return size in MB
        return msg.audio.size // 10 ** 6
    
    def get_document_id(self, msg):
        return msg.audio.id
    
    def is_allowed_filename(self, word):
        pat = re.compile(FILENAME_PATTERN)
        if word and re.match(pat, word):
            return True
        else:
            print(word)
            return False

    def char_normalization(self, char, input_string):

        return re.sub(rf'{char}+', char, input_string)

        
    def clean_and_format_string(self, input_string):
        # Replace space, _, and | with -
        transformed_string = re.sub(r'^\d+', '', input_string)
        transformed_string = transformed_string.replace('@', '-').replace('_', '-')\
                                            .replace('|', '-').replace('@', '-')\
                                            .replace('~', "-").replace('.', '-')\
                                            .replace("'", "-").replace(' ', '-')\
                                            .replace("&", "-")
        
        # Remove hyphens from the beginning of the string
        transformed_string = transformed_string.lstrip('-')
        
        # Replace multiple consecutive hyphens with a single hyphen
        transformed_string = self.char_normalization('-', transformed_string)
        
        return transformed_string

    def generate_filename(self):
        channel_username = self.channel["username"]
        date = self.date
        audio_title = ""
        audio_artist = ""

        if self.is_allowed_filename(self.title):
            audio_title = self.clean_and_format_string(self.title)
        if self.is_allowed_filename(self.performer):
            audio_artist = self.clean_and_format_string(self.performer)
        
        filename = str(self.id) + f"_{channel_username}_{audio_title}_{audio_artist}_{date}.{self.extension}"
        return self.char_normalization("_", filename)

    def get_edit_date(self, msg):
        if msg.edit_date:
            return msg.edit_date.strftime(DATE_FORMAT)
        return self.get_date(msg)
    
    def to_dict(self):
       return {
        "id": self.id,
        "title": self.title,
        "performer": self.performer,
        "duration": self.duration,
        "date": self.date,
        "author_name": self.author_name,
        "channel": self.channel,
        "msg_id": self.msg_id,
        "message": self.message,
        "filename": self.filename,
        "mime_type": self.mime_type,
        "edit_date": self.edit_date,
        "size" : self.size,
        "document_id" : self.document_id
    }

        


async def main():
    client = TelegramClient(SESSION_OBJ, API_ID, API_HASH, proxy=proxy)
    await client.start()
    channel = await client.get_entity(CHANNEL_USERNAME)
    async for msg in client.iter_messages(channel, min_id=MIN_MSG_ID, reverse=True, limit=DATA_FETCH_LIMIT):
        if not msg.audio:
            continue
        audio = AudioDetail(msg)
        if audio.duration <= DURATION_LIMIT:
            audio_detail_append(audio, data)
    dump_json(DATA_FILE_PATH, data )

asyncio.run(main())





