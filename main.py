import os
import yt_dlp
from pydub import AudioSegment
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext

# Funzione per scaricare il video in MP4 1080p
def download_video(url):
    # Percorso di salvataggio
    download_folder = 'downloads/'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Path al file dei cookies
    cookies_file = 'cookies.json'  # Sostituisci con il percorso corretto del tuo file cookies

    # Opzioni per yt-dlp
    ydl_opts = {
        'format': 'bestvideo[height<=1080]',  # Scarica il video migliore fino a 1080p + audio migliore
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),  # Percorso di salvataggio
        'cookiefile': cookies_file,  # Aggiungi qui il percorso del file dei cookies
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Estrai le informazioni e scarica il video
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = os.path.join(download_folder, f"{info_dict['title']}.mp4")  # Ottieni il percorso del file mp4
            return downloaded_file
        except Exception as e:
            raise Exception(f"Errore durante il download: {str(e)}")

# Funzione per scaricare l'audio e convertirlo in MP3 usando pydub
def download_audio(url):
    # Percorso di salvataggio
    download_folder = 'downloads/'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Path al file dei cookies
    cookies_file = 'cookies.json'  # Sostituisci con il percorso corretto del tuo file cookies

    # Opzioni per yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',  # Scarica solo l'audio migliore disponibile
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),  # Percorso di salvataggio
        'cookiefile': cookies_file,  # Aggiungi qui il percorso del file dei cookies
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Estrai le informazioni e scarica l'audio
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = os.path.join(download_folder, f"{info_dict['title']}.webm")  # Ottieni il percorso del file webm
            # Converti in MP3 usando pydub
            audio = AudioSegment.from_file(downloaded_file)
            mp3_file = os.path.join(download_folder, f"{info_dict['title']}.mp3")
            audio.export(mp3_file, format="mp3")  # Esporta come MP3
            os.remove(downloaded_file)  # Elimina il file webm
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
        # Creiamo i pulsanti per la scelta del formato
        keyboard = [
            [
                InlineKeyboardButton("Scarica MP4 (1080p)", callback_data=f"mp4:{user_message}"),
                InlineKeyboardButton("Scarica MP3", callback_data=f"mp3:{user_message}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Rispondi con i pulsanti per il formato
        await update.message.reply_text("Scegli il formato:", reply_markup=reply_markup)
    else:
        await update.message.reply_text('Per favore, invia un link valido di YouTube.')

# Funzione per gestire la risposta ai pulsanti e scaricare il file nel formato scelto
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Assicurati di usare await per rispondere alla callback

    # Otteniamo i dati dalla callback
    data = query.data
    
    # Controlla che i dati siano nel formato corretto
    if ":" not in data:
        await query.message.reply_text("Errore: i dati del pulsante sono errati.")
        return
    
    file_format, url = data.split(":", 1)  # Limita il split a due parti (nel caso ci siano ":" nell'URL)

    try:
        if file_format == "mp4":
            # Scarica il video in 1080p
            file_path = download_video(url)
        else:
            # Gestione per MP3
            file_path = download_audio(url)
        
        with open(file_path, 'rb') as f:
            # Invia il file all'utente
            await query.message.reply_document(f)

        # Elimina il file locale dopo averlo inviato
        os.remove(file_path)
        await query.message.reply_text(f"Il file {file_format.upper()} è stato inviato e rimosso dal server.")
    except Exception as e:
        await query.message.reply_text(f"Si è verificato un errore: {str(e)}")

# Funzione principale per avviare il bot
def main():
    # Inserisci il token del tuo bot
    TELEGRAM_API_TOKEN = '7644270647:AAGMEVmwyzAAnQHUqDAzc4pW10frsbkWtlY'

    # Crea l'applicazione del bot
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Aggiungi i gestori per i comandi e i messaggi
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))  # Gestisci il click sui pulsanti

    # Avvia il bot
    application.run_polling()

if __name__ == '__main__':
    main()
