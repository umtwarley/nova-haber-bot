import os
from keep_alive import keep_alive
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
from telebot import TeleBot, types
import asyncio

# keep-alive başlat
keep_alive()

# Ortam değişkenleri
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
channel_id = os.getenv("CHANNEL_ID")
source_channel = os.getenv("SOURCE_CHANNEL")

# Botlar
bot = TeleBot(bot_token)
client = TelegramClient('anon', api_id, api_hash).start(bot_token=bot_token)

# Medya galerisi geçici alan
media_gruplari = {}

@client.on(events.NewMessage(chats=source_channel))
async def yeni_haber(event):
    try:
        mesaj = event.message.message or ""

        # Galeri
        if event.message.grouped_id:
            grup_id = event.message.grouped_id
            if grup_id not in media_gruplari:
                media_gruplari[grup_id] = []
            medya_yolu = await event.message.download_media()
            if medya_yolu:
                media_gruplari[grup_id].append((medya_yolu, mesaj))

            await asyncio.sleep(3)
            if len(media_gruplari[grup_id]) > 1:
                media = []
                for yol, aciklama in media_gruplari[grup_id]:
                    media.append(types.InputMediaPhoto(media=open(yol, 'rb'), caption=aciklama if len(media) == 0 else None))
                bot.send_media_group(chat_id=channel_id, media=media)
                for yol, _ in media_gruplari[grup_id]:
                    os.remove(yol)
                del media_gruplari[grup_id]
            return

        # Tekil medya
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

# Railway uyumlu çalıştırma
print("✅ Bot bağlantısı sağlandı.")
client.run_until_disconnected()
