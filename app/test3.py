from yt_dlp import YoutubeDL
import random
import string

def generate_filename():
    letters = random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10)
    numbers = random.choices(string.digits, k=10)
    combined = letters + numbers
    random.shuffle(combined)
    result = ''.join(combined)
    return result

def download_tiktok_video(url):
    file_name = generate_filename()
    file_path = f'TikTok_video/{file_name}.mp4'

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  
        'outtmpl': f'{file_path}',         
        'merge_output_format': 'mp4',      
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return file_path

url = "https://vm.tiktok.com/ZMhGVM59t/"
path_to_video = download_tiktok_video(url)
print(f"Видео сохранено в: {path_to_video}")
