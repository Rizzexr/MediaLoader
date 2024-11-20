from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputFile
from yt_dlp import YoutubeDL
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import app.keyboards as kb
from aiogram.types import InputFile
from aiogram.types import FSInputFile
import os
import configparser
from moviepy.editor import VideoFileClip

import random
import string

router = Router()
USER_FILE = 'users.txt'
cookies_file = "cookies.json"


class Youtube(StatesGroup):
    url = State()

class Youtube_audio(StatesGroup):
    url = State()

class Tiktok(StatesGroup):
    url = State()

class Tiktok_audio(StatesGroup):
    url = State()

async def add_user_id(user_id: int):
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as file:
            user_ids = file.readlines()
    else:
        user_ids = []

    if f'{user_id}\n' not in user_ids:
        with open(USER_FILE, 'a') as file:
            file.write(f'{user_id}\n')


async def youtube_to_thumbnail(url):
    video_id = url.split("/")[-1].split("?")[0]
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

async def generate_filename():
    letters = random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10)
    numbers = random.choices(string.digits, k=10)
    combined = letters + numbers
    random.shuffle(combined)
    return ''.join(combined)
    
async def download_send_video(url):
    file_name = await generate_filename()
    file_path = f'YouTube_video/{file_name}.mp4'

    ydl_opts = {
        'format': 'best',  
        'cookies': cookies_file,
        'outtmpl': f'{file_path}', 
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return file_path


async def download_tiktok_video(url):
    file_name = await generate_filename()
    file_path = f'TikTok_video/{file_name}.mp4'

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  
        'outtmpl': f'{file_path}',            
        'merge_output_format': 'mp4',         
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return file_path


async def convert_mp4_to_mp3(path_to_video):
    try:
        
        output_file = os.path.splitext(path_to_video)[0] + ".mp3"
        
        
        video = VideoFileClip(path_to_video)
        
        
        video.audio.write_audiofile(output_file)
        
        print(f"Файл успешно сохранен как {output_file}")
        return output_file
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


# Обработчики

# Приветствие при старте бота
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'👋 Привет {message.from_user.first_name}. Я помогу тебе скачать видео с различных медиа ресурсов 🎥💾. Выбери соцсеть, чтобы начать', reply_markup=kb.call_menu)
    print("SM0001")
    
    user_id = message.from_user.id
    await add_user_id(user_id)

    config = configparser.ConfigParser()
    config.read('data.ini')

    if not config.has_section(f'{message.from_user.id}'):
        config.add_section(f'{message.from_user.id}')
        config.set(f'{message.from_user.id}', 'youtube', '0')
        config.set(f'{message.from_user.id}', 'tiktok', '0')

    with open('data.ini', 'w') as configfile:
        config.write(configfile)
        print("DB0001")



# YouTube

# Обоботчик нажатия > YouTube
@router.callback_query(F.data == 'menu_youtube')
async def inline1(callback: CallbackQuery):
    await callback.message.answer('Выбери режим:', reply_markup=kb.call_menu_youtube)

# Обоботчик нажатия > YouTube > Скачать видео
@router.callback_query(F.data == 'menu_youtube_video')
async def get_youtube_url(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Youtube.url)
    await callback.message.edit_text('💬 **Отправь ссылку на Видео/Shorts**', parse_mode="Markdown")

# Процесс загрузки > YouTube > Скачать видео
@router.message(Youtube.url)
async def chek_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    data = await state.get_data()

    url = data["url"]

    await state.clear()

    await message.answer('🚀 **Уже скачиваю!** ⬇️', parse_mode="Markdown")

    path_to_video = await download_send_video(url)

    await message.answer_video(video=FSInputFile(path_to_video))
    os.remove(path_to_video)
    await message.answer('**Вот и ваше видео!)** 🎬\n\nЧто-то еще? 💭', parse_mode="Markdown", reply_markup=kb.call_menu)

    config = configparser.ConfigParser()
    config.read('data.ini')

    subsection_value = config.get(f'{message.from_user.id}', 'youtube')
    current_value_int = int(subsection_value)
    new_value = current_value_int + 1

    config.set(f'{message.from_user.id}', 'youtube', str(new_value))

    with open('data.ini', 'w') as configfile:
        config.write(configfile)

# Обоботчик нажатия > YouTube > Скачать аудио
@router.callback_query(F.data == 'menu_youtube_audio')
async def get_youtube_url(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Youtube_audio.url)
    await callback.message.edit_text('💬 **Отправь ссылку на видео** и я извлеку из него звук', parse_mode="Markdown")

# Процесс загрузки > YouTube > Скачать аудио
@router.message(Youtube_audio.url)
async def chek_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    data = await state.get_data()

    url = data["url"]

    await state.clear()

    await message.answer('🚀 **Уже скачиваю!** ⬇️', parse_mode="Markdown")
    path_to_video = await download_send_video(url)
    path_to_audio = await convert_mp4_to_mp3(path_to_video)

    await message.answer_audio(audio=FSInputFile(path_to_audio))
    os.remove(path_to_video)
    os.remove(path_to_audio)
    await message.answer('**Вот и ваше аудио!)** 🎬\n\nЧто-то еще? 💭', parse_mode="Markdown", reply_markup=kb.call_menu)

    config = configparser.ConfigParser()
    config.read('data.ini')

    subsection_value = config.get(f'{message.from_user.id}', 'youtube')
    current_value_int = int(subsection_value)
    new_value = current_value_int + 1

    config.set(f'{message.from_user.id}', 'youtube', str(new_value))

    with open('data.ini', 'w') as configfile:
        config.write(configfile)



# TikTok

# Обоботчик нажатия > TikTok
@router.callback_query(F.data == 'menu_tiktok')
async def inline1(callback: CallbackQuery):
    await callback.message.answer('Выбери режим:', reply_markup=kb.call_menu_tiktok)

# Обоботчик нажатия > Tiktok > Скачать видео
@router.callback_query(F.data == 'menu_tiktok_video')
async def get_youtube_url(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Tiktok.url)
    await callback.message.edit_text('💬 **Отправь ссылку на видео**', parse_mode="Markdown")

# Процесс загрузки > TikTok > Скачать видео
@router.message(Tiktok.url)
async def chek_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    data = await state.get_data()

    url = data["url"]

    await state.clear()

    await message.answer('🚀 **Уже скачиваю!** ⬇️', parse_mode="Markdown")
    path_to_video = await download_tiktok_video(url)

    await message.answer_video(video=FSInputFile(path_to_video))
    os.remove(path_to_video)
    await message.answer('**Вот и ваше видео!)** 🎬\n\nЧто-то еще? 💭', parse_mode="Markdown", reply_markup=kb.call_menu)

    config = configparser.ConfigParser()
    config.read('data.ini')

    subsection_value = config.get(f'{message.from_user.id}', 'tiktok')
    current_value_int = int(subsection_value)
    new_value = current_value_int + 1

    config.set(f'{message.from_user.id}', 'tiktok', str(new_value))

    with open('data.ini', 'w') as configfile:
        config.write(configfile)

# Обоботчик нажатия > TikTok > Скачать аудио
@router.callback_query(F.data == 'menu_tiktok_audio')
async def get_youtube_url(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Tiktok_audio.url)
    await callback.message.edit_text('💬 **Отправь ссылку на видео** и я извлеку из него звук', parse_mode="Markdown")

# Процесс загрузки >TikTok > Скачать аудио
@router.message(Tiktok_audio.url)
async def chek_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    data = await state.get_data()

    url = data["url"]

    await state.clear()

    await message.answer('🚀 **Уже скачиваю!** ⬇️', parse_mode="Markdown")
    path_to_video = await download_tiktok_video(url)
    path_to_audio = await convert_mp4_to_mp3(path_to_video)

    await message.answer_audio(audio=FSInputFile(path_to_audio))
    os.remove(path_to_video)
    os.remove(path_to_audio)
    await message.answer('**Вот и ваше аудио!)** 🎬\n\nЧто-то еще? 💭', parse_mode="Markdown", reply_markup=kb.call_menu)

    config = configparser.ConfigParser()
    config.read('data.ini')

    subsection_value = config.get(f'{message.from_user.id}', 'tiktok')
    current_value_int = int(subsection_value)
    new_value = current_value_int + 1

    config.set(f'{message.from_user.id}', 'tiktok', str(new_value))

    with open('data.ini', 'w') as configfile:
        config.write(configfile)



# Другое

# Показ статистики
@router.callback_query(F.data == 'my_statistics')
async def get_youtube_url(callback: CallbackQuery, state: FSMContext):

    config = configparser.ConfigParser()
    config.read('data.ini')

    current_value_tiktok = int(config.get(f'{callback.from_user.id}', 'tiktok'))
    current_value_youtube = int(config.get(f'{callback.from_user.id}', 'youtube'))

    full = current_value_tiktok + current_value_youtube

    await callback.message.edit_text(f'⚙️ **Ваша статистика:**\nВсего скачиваний: {full}\nTikTok: {current_value_tiktok}\nYouTube: {current_value_youtube}', parse_mode="Markdown", reply_markup=kb.call_menu)