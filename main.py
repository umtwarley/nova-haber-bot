from telethon import TelegramClient, events
import telebot
import os
import time
from telethon.tl.types import MessageMediaPhoto
from keep_alive import keep_alive

keep_alive()

# Ortam değişkenleri
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
channel_id = os.environ.get("CHANNEL_ID")
source_channel = os.environ.get("SOURCE_CHANNEL")

# Telebot ve Telethon başlat
bot = telebot.TeleBot(bot_token)
client = TelegramClient('anon', api_id, api_hash)

# BOT TOKEN İLE GİRİŞ
async def main():
    await client.start(bot_token=bot_token)

    media_gruplari = {}

    @client.on(events.NewMessage(chats=source_channel))
    async def yeni_haber(event):
        try:
            mesaj = event.message.message or ""

            if event.message.grouped_id:
                grup_id = event.message.grouped_id
                if grup_id not in media_gruplari:
                    media_gruplari[grup_id] = []
                medya_yolu = await event.message.download_media()
                if medya_yolu:
                    media_gruplari[grup_id].append((medya_yolu, mesaj))

                await client.loop.run_in_executor(None, time.sleep, 3)
                if len(media_gruplari[grup_id]) > 1:
                    media = []
                    for yol, aciklama in media_gruplari[grup_id]:
                        media.append(telebot.types.InputMediaPhoto(media=open(yol, 'rb'), caption=aciklama if len(media) == 0 else None))
                    bot.send_media_group(chat_id=channel_id, media=media)
                    for yol, _ in media_gruplari[grup_id]:
                        os.remove(yol)
                    del media_gruplari[grup_id]
                return

            if event.message.media:
                medya_yolu = await event.message.download_media()
                if medya_yolu:
                    if medya_yolu.lower().endswith(('.mp4', '.mov', '.mkv')):
                        with open(medya_yolu, 'rb') as dosya:
                            bot.send_video(channel_id, video=dosya, caption=mesaj, parse_mode="HTML")
                    else:
                        with open(medya_yolu, 'rb') as dosya:
                            bot.send_photo(channel_id, photo=dosya, caption=mesaj, parse_mode="HTML")
                    os.remove(medya_yolu)

            elif mesaj:
                bot.send_message(channel_id, mesaj)

        except Exception as e:
            print("❌ Hata:", e)

    await client.run_until_disconnected()

import asyncio
asyncio.run(main())
