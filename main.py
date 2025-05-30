from telethon import TelegramClient, events
import telebot
import os
import time
from PIL import Image
from telethon.tl.types import MessageMediaPhoto
from keep_alive import keep_alive

keep_alive()

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
channel_id = os.environ.get("CHANNEL_ID")
source_channel = os.environ.get("SOURCE_CHANNEL")

bot = telebot.TeleBot(bot_token)
client = TelegramClient('gdh_izleyici', api_id, api_hash)

media_gruplari = {}

def logolu_gorsel_uret(dosya_yolu):
    try:
        img = Image.open(dosya_yolu).convert("RGBA")
        logo = Image.open("nsp_logo.png").convert("RGBA")
        oran = 0.15
        logo_boyut = (int(img.width * oran), int(logo.height * img.width * oran / logo.width))
        logo = logo.resize(logo_boyut)
        konum = (5, 5)
        img.paste(logo, konum, logo)
        yeni_yol = "logolu_" + os.path.basename(dosya_yolu).rsplit('.', 1)[0] + ".png"
        img.save(yeni_yol, format="PNG")
        return yeni_yol
    except Exception as e:
        print("❌ Logo eklenirken hata:", e)
        return dosya_yolu

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
                yeni_yol = logolu_gorsel_uret(medya_yolu)
                media_gruplari[grup_id].append((yeni_yol, mesaj))
            await client.loop.run_in_executor(None, time.sleep, 3)
            if len(media_gruplari[grup_id]) > 1:
                media = []
                for yol, aciklama in media_gruplari[grup_id]:
                    media.append(telebot.types.InputMediaPhoto(media=open(yol, 'rb'), caption=aciklama if len(media) == 0 else None))
                bot.send_media_group(chat_id=channel_id, media=media)
                print("🖼 Galeri gönderildi.")
                for yol, _ in media_gruplari[grup_id]:
                    if os.path.exists(yol):
                        os.remove(yol)
                del media_gruplari[grup_id]
            return
        if event.message.media:
            medya_yolu = await event.message.download_media()
            if medya_yolu:
                logolu_yol = logolu_gorsel_uret(medya_yolu)
                if logolu_yol.lower().endswith(('.mp4', '.mov', '.mkv')):
                    with open(logolu_yol, 'rb') as dosya:
                        bot.send_video(channel_id, video=dosya, caption=mesaj, parse_mode="HTML")
                    print("🎥 Video gönderildi.")
                else:
                    with open(logolu_yol, 'rb') as dosya:
                        bot.send_photo(channel_id, photo=dosya, caption=mesaj, parse_mode="HTML")
                    print("📸 Fotoğraf gönderildi.")
                for yol in [logolu_yol, medya_yolu]:
                    if os.path.exists(yol):
                        os.remove(yol)
        elif mesaj:
            bot.send_message(channel_id, mesaj)
            print("📝 Metin gönderildi:", mesaj[:50])
    except Exception as e:
        print("❌ Hata:", e)

client.start()
client.run_until_disconnected()
