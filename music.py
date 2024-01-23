import os
import time
from typing import Tuple
import yt_dlp as youtube_dl
from telegram import Update
from telegram.ext import CallbackContext, ContextTypes

current_dir = os.path.dirname(os.path.abspath(__file__))

def download_audio(url: str) -> Tuple[str, str]:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(playlist_title)s/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ignoreerrors': True,  # Ignore errors
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return 'downloads/' + info_dict['title'] + '/', info_dict["title"]

async def send_all_audio(update: Update, context: CallbackContext, file_path: str) -> None:
    while True:
        for (dirpath, dirnames, filenames) in os.walk(file_path):
            if len(filenames) == 0:
                return
            for filename in filenames:
                filename: str = filename.replace('webm', 'mp3')
                # print(f'filename: {filename}')
                if filename.endswith('.part'):
                    continue    # skip files failed to download
                full_file_path = file_path + filename
                try:
                    print('sending audio: ', filename)
                    with open(full_file_path, 'rb') as audio_file:
                        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio_file, 
                                                        write_timeout=120, connect_timeout=120, pool_timeout=120)
                    os.remove(full_file_path)
                    time.sleep(1)
                except Exception as e:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(e)+" for "+ filename)
                    print(e, filename)

async def play(update: Update, context:  ContextTypes.DEFAULT_TYPE) -> None:
    print(context.args)
    music_link: str = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Downloading mp3 from playlist {music_link}')
    print(music_link)
    try:
        all_success = True
        file_path, title = download_audio(music_link)
        print(f'file path: {file_path}')
        await send_all_audio(update, context, file_path)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Downloaded all mp3s from playlist {title}')
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
        print(e)
    

def test_single_song():
    url = 'https://youtu.be/5RaU8K8sLTM?si=r0eajzNcZyDZSY4V'
    print(download_audio((url)))

def test_playlist():
    url = 'https://www.youtube.com/playlist?list=PLVqJ1WxX9VeDV98868qcdZSISwDV468Pc'
    print(download_audio((url)))

def test_error_playlist():
    url = 'https://youtube.com/playlist?list=PLVqJ1WxX9VeCu54yyAH83MYdW30nl7Fkv&si=eVA156cU2l2adPi9'
    print(download_audio((url)))

if __name__ == '__main__':
    # test_single_song()
    # test_playlist()
    test_error_playlist()