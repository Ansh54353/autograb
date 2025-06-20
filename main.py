from telethon import TelegramClient, events
import asyncio
import random
import os
from keep_alive import keep_alive

# Load from environment variables
API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
PHONE_NUMBER = os.environ['PHONE_NUMBER']
SESSION_NAME = 'waifu_bot_fixed'

# Chat IDs
SOURCE_GROUP = int(os.environ['SOURCE_GROUP'])  # e.g., -1002569925306
TARGET_GROUP = os.environ['TARGET_GROUP']       # e.g., "@SourceZeo"
WAIFU_BOT_USERNAME = '@collect_waifu_cheats_bot'
SLAVE_BOT_USERNAME = '@slave_waifu_bot'

DELAYS = {
    'maxx': (5, 6),
    'minn': (3, 4)
}

REQUIRED_TEXT = "✨ ᴀ ɴᴇᴡ ᴄʜᴀʀᴀᴄᴛᴇʀ ʜᴀꜱ ᴀᴘᴘᴇᴀʀᴇᴅ! ✨\nᴜꜱᴇ /grab (ɴᴀᴍᴇ) ᴛᴏ ᴀᴅᴅ ɪᴛ ɪɴ ʏᴏᴜʀ ʜᴀʀᴇᴍ."

class WaifuProcessor:
    def __init__(self):
        self.busy = False
        self.current_delay = DELAYS['minn']
        self.source_chat = None
        self.last_waifu_msg = None

    async def start(self):
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        await self.client.start(PHONE_NUMBER)
        print("✅ Bot is running!")

        global SLAVE_BOT_ID, WAIFU_BOT_ID
        slave = await self.client.get_entity(SLAVE_BOT_USERNAME)
        waifu = await self.client.get_entity(WAIFU_BOT_USERNAME)
        SLAVE_BOT_ID = slave.id
        WAIFU_BOT_ID = waifu.id

        @self.client.on(events.NewMessage(chats=SOURCE_GROUP))
        async def handler(event):
            text = event.raw_text or ""
            if (event.sender_id == SLAVE_BOT_ID and event.message.photo and REQUIRED_TEXT in text):
                if not self.busy:
                    self.busy = True
                    self.source_chat = event.chat_id
                    try:
                        forwarded = await event.forward_to(TARGET_GROUP)
                        await asyncio.sleep(random.uniform(*self.current_delay) * 0.3)
                        self.last_waifu_msg = await self.client.send_message(
                            TARGET_GROUP, ".waifu", reply_to=forwarded.id
                        )
                    except Exception as e:
                        print(f"⚠️ Processing error: {str(e)}")
                        self.busy = False

        @self.client.on(events.NewMessage(from_users=WAIFU_BOT_ID, chats=TARGET_GROUP))
        async def waifu_response_handler(event):
            if self.last_waifu_msg and event.is_reply and event.reply_to_msg_id == self.last_waifu_msg.id:
                response_text = event.raw_text.strip()
                if "not found" in response_text.lower():
                    print("❌ Humanizer not found. Skipping...")
                    self.last_waifu_msg = None
                    self.busy = False
                    return
                if "Humanizer:" in response_text:
                    humanizer = response_text.split("Humanizer:", 1)[1].strip().splitlines()[0]
                    await self.client.send_message(self.source_chat, humanizer)
                    print(f"✅ Sent Humanizer: {humanizer}")
                    self.last_waifu_msg = None
                    self.busy = False

        @self.client.on(events.NewMessage(pattern=r'^\.(maxx|minn)$'))
        async def set_delay(event):
            mode = event.pattern_match.group(1)
            self.current_delay = DELAYS[mode]
            await event.reply(f"⏱️ Mode set to {mode} ({self.current_delay[0]}-{self.current_delay[1]}s)")

        await self.client.run_until_disconnected()

async def main():
    keep_alive()  # Start web server for keep-alive ping
    bot = WaifuProcessor()
    await bot.start()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped")
