import os
import logging
import zipfile
import shutil
from telethon import Button, TelegramClient, events
from telethon.tl.types import DocumentAttributeFilename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - [%(levelname)s] - %(message)s'
)
LOGGER = logging.getLogger(__name__)

# Initialize the Telegram client
api_id = int(os.getenv("APP_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("TOKEN")
Jarvis = TelegramClient('client', api_id, api_hash).start(bot_token=bot_token)

# Dictionary to keep track of user files
user_files = {}

def zip_files(files: list[str], zip_file_path: str) -> bool:
    try:
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            for file in files:
                zip_file.write(file, os.path.basename(file))
        return True
    except Exception as e:
        LOGGER.error(f"Error creating zip file: {e}")
        return False

@Jarvis.on(events.NewMessage(pattern="^/zip$"))
async def start_zip_command(event: events.NewMessage.Event):
    user_id = event.sender_id
    user_files[user_id] = []
    await event.reply("Please send all ᴘᴅғ files one by one. When done, use /confirm to zip them.")

@Jarvis.on(events.NewMessage(func=lambda e: e.is_private and e.document))
async def collect_pdf(event: events.NewMessage.Event):
    user_id = event.sender_id
    if user_id in user_files:
        if isinstance(event.document.attributes[0], DocumentAttributeFilename) and event.document.mime_type == "application/pdf":
            file_path = await event.client.download_media(event.document)
            user_files[user_id].append(file_path)
            await event.reply(f"Added `{event.document.attributes[0].file_name}` to the zip list.")
        else:
            await event.reply("Please send only ᴘᴅғ files.")

@Jarvis.on(events.NewMessage(pattern="^/confirm$"))
async def confirm_zip(event: events.NewMessage.Event):
    user_id = event.sender_id
    if user_id in user_files and user_files[user_id]:
        zip_file_path = f"{user_id}_files.zip"
        if zip_files(user_files[user_id], zip_file_path):
            await event.reply(file=zip_file_path)
            os.remove(zip_file_path)
            for file_path in user_files[user_id]:
                os.remove(file_path)
            del user_files[user_id]
            await event.reply("Your files have been zipped and sent!")
        else:
            await event.reply("There was an error creating the zip file.")
    else:
        await event.reply("You haven't added any files to zip. Use /zip to start.")

def unzip_file(zip_file_path: str, output_folder: str) -> bool:
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            zip_file.extractall(output_folder)
        return True
    except Exception as e:
        LOGGER.error(f"Error unzipping file: {e}")
        return False

@Jarvis.on(events.NewMessage(pattern="^/unzip$"))
async def unzip_command(event: events.NewMessage.Event):
    if event.is_reply:
        reply_message = await event.get_reply_message()
        if reply_message and reply_message.document and reply_message.document.mime_type == "application/zip":
            zip_file_path = await event.client.download_media(reply_message)
            output_folder = f"{zip_file_path}_unzipped"
            os.makedirs(output_folder, exist_ok=True)
            if unzip_file(zip_file_path, output_folder):
                for root, _, files in os.walk(output_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        await event.reply(file=file_path)
                shutil.rmtree(output_folder)
                os.remove(zip_file_path)
            else:
                await event.reply("There was an error unzipping the file.")
        else:
            await event.reply("Reply to a zip file with /unzip to extract its contents.")
    else:
        await event.reply("Please reply to a zip file with /unzip to extract its contents.")

@Jarvis.on(events.NewMessage(pattern="^/start$"))
async def start(event: events.NewMessage.Event):
    await event.reply(
        "**I ᴀᴍ ᴛʜᴇ Zɪᴘ Cᴏɴᴠᴇʀᴛᴇʀ Bᴏᴛ, ʏᴏᴜʀ ᴇғғɪᴄɪᴇɴᴛ ᴀssɪsᴛᴀɴᴛ ғᴏʀ ᴍᴀɴᴀɢɪɴɢ ᴘᴅғ ғɪʟᴇs.**\n\n"
        "**I ᴡɪʟʟ ʜᴇʟᴘ ʏᴏᴜ ᴇғғᴏʀᴛʟᴇssʟʏ ᴢɪᴘ ᴍᴜʟᴛɪᴘʟᴇ ᴘᴅғ ғɪʟᴇs ᴛᴏɢᴇᴛʜᴇʀ ᴏʀ ᴜɴᴢɪᴘ ᴛʜᴇᴍ ғᴏʀ ᴇᴀsʏ ᴀᴄᴄᴇss.**\n\n"
        "**Usᴇ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅs:**\n\n"
        "**๏** `/ᴢɪᴘ` - Sᴛᴀʀᴛ ᴛʜᴇ ᴘʀᴏᴄᴇss ᴏғ ᴄᴏʟʟᴇᴄᴛɪɴɢ ᴘᴅғ ғɪʟᴇs ᴛᴏ ᴢɪᴘ.\n"
        "**๏** `/ᴄᴏɴғɪʀᴍ` - Zɪᴘ ᴀʟʟ ᴄᴏʟʟᴇᴄᴛᴇᴅ ᴘᴅғ ғɪʟᴇs ᴀɴᴅ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ᴢɪᴘᴘᴇᴅ ғɪʟᴇ.\n"
        "**๏** `/ᴜɴᴢɪᴘ` - Rᴇᴘʟʏ ᴛᴏ ᴀ ᴢɪᴘ ғɪʟᴇ ᴛᴏ ᴇxᴛʀᴀᴄᴛ ɪᴛs ᴄᴏɴᴛᴇɴᴛs.",
        link_preview=False,
        buttons=[
            [Button.url("ᴏᴡɴᴇʀ", url="https://t.me/JARVIS_V2")],
            [Button.url("sᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ", url="https://t.me/JARVIS_V_SUPPORT")]
        ]
    )

# Run the Telegram client
Jarvis.run_until_disconnected()
