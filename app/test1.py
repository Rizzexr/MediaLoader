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

def download_send_video(url):
    file_name = generate_filename()
    file_path = f'YouTube_video/{file_name}.mp4'

    ydl_opts = {
        'format': 'best',  
        'outtmpl': f'{file_path}', 
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return file_path

url = "https://youtu.be/dQw4w9WgXcQ?si=rxwi_XUX82YQCDap"
path_to_video = download_send_video(url)
print(path_to_video)
