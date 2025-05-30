import os
import time
import asyncio
from telethon import TelegramClient, events
from telebot import TeleBot, types
from telethon.tl.types import MessageMediaPhoto

# .env'den değerleri al
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
channel_id = os.getenv("CHANNEL_ID")  # Örnek: @novasporhaber
source_channel = os.getenv("SOURCE_CHANNEL")  # Örnek: gdhspor

# Bot başlat
bot = TeleBot(bot_token)
client = TelegramClient("bot", api_id, api_hash)

media_gruplari = {}

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    mesaj = event.message.message or ""

    if event.message.grouped_id:
        grup_id = event.message.grouped_id
        if grup_id not in media_gruplari:
            media_gruplari[grup_id] = []
        yol = await event.message.download_media()
        if yol:
            media_gruplari[grup_id].append((yol, mesaj))
        await asyncio.sleep(3)
        if len(media_gruplari[grup_id]) > 1:
            medya = []
            for idx, (yol, aciklama) in enumerate(media_gruplari[grup_id]):
                medya.append(types.InputMediaPhoto(open(yol, 'rb'), caption=aciklama if idx == 0 else None))
            bot.send_media_group(channel_id, medya)
            for yol, _ in media_gruplari[grup_id]:
                os.remove(yol)
            del media_gruplari[grup_id]
        return

    if event.message.media:
        yol = await event.message.download_media()
        if yol:
            if yol.endswith(('.mp4', '.mov')):
                with open(yol, 'rb') as dosya:
                    bot.send_video(channel_id, dosya, caption=mesaj)
            else:
                with open(yol, 'rb') as dosya:
                    bot.send_photo(channel_id, dosya, caption=mesaj)
            os.remove(yol)
    elif mesaj:
        bot.send_message(channel_id, mesaj)

async def main():
    await client.start(bot_token=bot_token)
    print("✅ Bot bağlantısı sağlandı.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Başlatma hatası: {e}")
        time.sleep(5)
