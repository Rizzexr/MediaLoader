from moviepy.editor import VideoFileClip

def convert_mp4_to_mp3(input_file, output_file):
    try:
        video = VideoFileClip(input_file)
        video.audio.write_audiofile(output_file)
        print(f"Файл успешно сохранен как {output_file}")
    except Exception as e:
        print(f"Ошибка: {e}")

convert_mp4_to_mp3("video.mp4", "audio.mp3")
