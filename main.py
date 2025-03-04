import os
import yt_dlp
from pydub import AudioSegment
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext

# Funzione per scaricare il video in MP4 1080p
def download_video(url):
    download_folder = 'downloads/'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    cookies_file = 'cookies.json'

    ydl_opts = {
        'format': 'bestvideo[height<=1080]',  # Video migliore fino a 1080p
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'cookiefile': cookies_file,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = os.path.join(download_folder, f"{info_dict['title']}.mp4")
            return downloaded_file
        except Exception as e:
            raise Exception(f"Errore durante il download: {str(e)}")

# Funzione per scaricare l'audio e convertirlo in MP3
def download_audio(url):
    download_folder = 'downloads/'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    cookies_file = 'cookies.json'

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'cookiefile': cookies_file,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = os.path.join(download_folder, f"{info_dict['title']}.webm")
            audio = AudioSegment.from_file(downloaded_file)
            mp3_file = os.path.join(download_folder, f"{info_dict['title']}.mp3")
            audio.export(mp3_file, format="mp3")
            os.remove(downloaded_file)
            return mp3_file
        except Exception as e:
            raise Exception(f"Errore durante il download o la conversione: {str(e)}")

# Funzione di comando start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Ciao! Invia un link di YouTube per scaricare il video o la musica.')

# Funzione per gestire il link e inviare i pulsanti per la scelta del formato
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    if 'youtube.com' in user_message or 'youtu.be' in user_message:
        keyboard = [
            [
                InlineKeyboardButton("Scarica MP4 (1080p)", callback_data=f"mp4:{user_message}"),
                InlineKeyboardButton("Scarica MP3", callback_data=f"mp3:{user_message}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Scegli il formato:", reply_markup=reply_markup)
    else:
        await update.message.reply_text('Per favore, invia un link valido di YouTube.')

# Funzione per gestire la risposta ai pulsanti e scaricare il file
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data
    
    if ":" not in data:
        await query.message.reply_text("Errore: i dati del pulsante sono errati.")
        return
    
    file_format, url = data.split(":", 1)

    try:
        if file_format == "mp4":
            file_path = download_video(url)
        else:
            file_path = download_audio(url)
        
        with open(file_path, 'rb') as f:
            await query.message.reply_document(f)

        os.remove(file_path)
        await query.message.reply_text(f"Il file {file_format.upper()} è stato inviato e rimosso dal server.")
    except Exception as e:
        await query.message.reply_text(f"Si è verificato un errore: {str(e)}")

# Funzione principale per avviare il bot
def main():
    TELEGRAM_API_TOKEN = 'TOKEN'

    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()
