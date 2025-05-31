import os
import time
from typing import Tuple
from pytubefix import YouTube, Playlist
from telegram import Update
from telegram.ext import CallbackContext, ContextTypes

current_dir = os.path.dirname(os.path.abspath(__file__))


def download_audio(url: str, is_playlist: bool) -> Tuple[str, str]:
    try:
        if is_playlist:
            # Handle playlist
            playlist = Playlist(url)
            playlist_title = playlist.title or "Unknown_Playlist"
            # Clean the title for use as folder name
            playlist_title = "".join(c for c in playlist_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            download_path = f"downloads/{playlist_title}/"
            os.makedirs(download_path, exist_ok=True)
            
            for video in playlist.videos:
                try:
                    # Get the best audio stream
                    audio_stream = video.streams.filter(only_audio=True).order_by('abr').desc().first()
                    if audio_stream:
                        # Clean the title for filename
                        safe_title = "".join(c for c in video.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        filename = f"{safe_title}.{audio_stream.subtype}"
                        audio_stream.download(output_path=download_path, filename=filename)
                except Exception as e:
                    print(f"Error downloading video {video.watch_url}: {e}")
                    continue
            
            return download_path, playlist_title
        else:
            # Handle single video with OAuth for better reliability
            yt = YouTube(
                url,
                use_oauth=True,
                allow_oauth_cache=True
            )
            download_path = "downloads/NA/"
            os.makedirs(download_path, exist_ok=True)
            
            # Get the best audio stream
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            if audio_stream:
                # Clean the title for filename
                safe_title = "".join(c for c in yt.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title}.{audio_stream.subtype}"
                audio_stream.download(output_path=download_path, filename=filename)
            
            return download_path, yt.title
            
    except Exception as e:
        print(f"Error in download_audio: {e}")
        raise e


async def send_all_audio(
    update: Update, context: CallbackContext, file_path: str
) -> None:
    for i in range(100):
        for dirpath, dirnames, filenames in os.walk(file_path):
            for filename in filenames:
                # Handle different audio formats that pytube might download
                if filename.endswith(".part"):
                    continue  # skip files failed to download
                
                # Check if it's an audio file
                if not any(filename.lower().endswith(ext) for ext in ['.mp3', '.mp4', '.webm', '.m4a', '.aac']):
                    continue
                    
                full_file_path = os.path.join(file_path, filename)
                try:
                    print("sending audio: ", filename)
                    with open(full_file_path, "rb") as audio_file:
                        await context.bot.send_audio(
                            chat_id=update.effective_chat.id,
                            audio=audio_file,
                            write_timeout=120,
                            connect_timeout=120,
                            pool_timeout=120,
                        )
                    os.remove(full_file_path)
                    time.sleep(1)
                    if len(filenames) == 0:
                        return
                    else:
                        print(f"send all audio trail: {i}")
                        print("filenames: ", filenames)
                except Exception as e:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=str(e) + " for " + filename,
                    )
                    print(e, filename)
    return Exception("Retry error!")


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(context.args)
    music_link: str = update.message.text
    is_list = "list" in music_link
    downloading_msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Downloading mp3 from{" playlist" if is_list else ""}: {music_link}',
    )

    print(music_link)
    try:
        all_success = True
        file_path, title = download_audio(music_link, is_list)
        print(f"file path: {file_path}")
        await send_all_audio(update, context, file_path)
        done_msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Downloaded all mp3 from{" playlist" if is_list else ""} {title}',
        )
        time.sleep(10)
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=update.message.id
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=downloading_msg.id
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=done_msg.id
        )
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
        print(e)


def test_single_song():
    url = "https://youtu.be/5RaU8K8sLTM?si=r0eajzNcZyDZSY4V"
    print(download_audio(url, False))


def test_playlist():
    url = "https://www.youtube.com/playlist?list=PLVqJ1WxX9VeDV98868qcdZSISwDV468Pc"
    print(download_audio(url, True))


def test_error_playlist():
    url = "https://youtube.com/playlist?list=PLVqJ1WxX9VeCu54yyAH83MYdW30nl7Fkv&si=eVA156cU2l2adPi9"
    print(download_audio(url, True))


if __name__ == "__main__":
    test_single_song()
    test_playlist()
    # test_error_playlist()
