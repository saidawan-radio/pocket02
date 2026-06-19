from telethon import TelegramClient
from telethon.tl.types import Message
from AudioDetail import AudioDetail



def get_github_raw_url(filename, repo_owner, repo_name, branch='main'):

    filename = filename.strip('/').replace('\\', '/')
    
    raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{filename}"
    
    return raw_url

def add_github_raw_url_to_detail(detail:dict, filename, repo_owner, repo_name, branch='main'):
    
    raw_url = get_github_raw_url(filename, repo_owner, repo_name, branch)
    
    detail["github_url"] = raw_url
    return detail
    
def add_opus_extension(filename:str):
    return filename + ".opus"

async def get_msg_by_audio_detail(client:TelegramClient, chat, audio:AudioDetail):

    msg = await client.get_messages(chat, ids=int(audio.msg_id))
    return msg

async def downoad_audio_by_msg(msg:Message, file_path:str, file_name:str):
    if hasattr(msg, "audio") and msg.audio:
        file = f"{file_path}/{file_name}"
        await msg.download_media(file=file)

async def download_audio_by_audio_detail(client:TelegramClient, chat, audio:AudioDetail, path:str):
    msg = await get_msg_by_audio_detail(client, chat, audio)
    await downoad_audio_by_msg(msg, path, audio.filename)
    
async def download_all_audio_detail(client:TelegramClient, chat, data, downlaod_path:str):
    for detail in data["audio_info"].values():
        audio = AudioDetail.from_dict(detail)
        await download_audio_by_audio_detail(client, chat, audio, downlaod_path)
        
async def download_audio_by_internal_id(client:TelegramClient, chat, data:str, intid, download_path:str ):
    detail = data["audio_info"][str(intid)] if data["audio_info"][str(intid)] else None
    if detail:
        audio = AudioDetail.from_dict(detail)
        await download_audio_by_audio_detail(client, chat, audio, download_path)


