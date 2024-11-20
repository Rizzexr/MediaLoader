from aiogram import F, Router
from aiogram.filters import CommandStart, Command
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

class Instagram(StatesGroup):
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

async def generate_filename():
    letters = random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10)
    numbers = random.choices(string.digits, k=10)
    combined = letters + numbers
    random.shuffle(combined)
    return ''.join(combined)
    
async def download_send_video(url):
    try:
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
    except Exception as e:
        print("Произошла ошибка. Код ошибки: DV0001")


async def download_tiktok_video(url):
    try:
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

    except Exception as e:
        print("Произошла ошибка. Код ошибки: DV0002")


async def convert_mp4_to_mp3(path_to_video):
    try:
        
        output_file = os.path.splitext(path_to_video)[0] + ".mp3"
        
        
        video = VideoFileClip(path_to_video)
        
        
        video.audio.write_audiofile(output_file)
        
        print(f"Файл успешно сохранен как {output_file}")
        return output_file
    except Exception as e:
        print("Произошла ошибка. Код ошибки: DF0003")

        
async def download_instagram_video(url):
    try:
        file_name = await generate_filename()
        output_folder = 'Instagram_videos'
        file_path = os.path.join(output_folder, f'{file_name}.mp4')

        ydl_opts = {
            'format': 'best',  
            'outtmpl': file_path,                
            'merge_output_format': 'mp4',      
            'quiet': False                      
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print(f"Видео успешно загружено: {file_path}")
        return file_path

    except Exception as e:
        print(f"Произошла ошибка. Код ошибки: DV0002\nДетали: {e}")
        return None



# Обработчики

# Приветствие при старте бота
@router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        await message.answer(f'👋 Привет {message.from_user.first_name}. Я помогу тебе скачать видео с различных медиа ресурсов 🎥💾. Выбери соцсеть, чтобы начать', reply_markup=kb.call_menu)

        user_id = message.from_user.id
        await add_user_id(user_id)

        config = configparser.ConfigParser()
        config.read('data.ini')

        if not config.has_section(f'{message.from_user.id}'):
            config.add_section(f'{message.from_user.id}')
            config.set(f'{message.from_user.id}', 'youtube', '0')
            config.set(f'{message.from_user.id}', 'tiktok', '0')
            config.set(f'{message.from_user.id}', 'instagram', '0')

        with open('data.ini', 'w') as configfile:
            config.write(configfile)
    
    except Exception as e:
        print("Произошла ошибка. Код ошибки: HP0001")


@router.message(Command('stat'))
async def get_help(message: Message):

    if message.from_user.id == 1474806847:
        config = configparser.ConfigParser()
        config.read('data.ini')

        total_youtube = 0
        total_tiktok = 0

        for section in config.sections():
            youtube = config.getint(section, 'youtube', fallback=0)
            tiktok = config.getint(section, 'tiktok', fallback=0)

            total_youtube += youtube
            total_tiktok += tiktok

        await message.answer(f'Статистика:\nВсего: {total_youtube + total_tiktok}\nYouTube: {total_youtube}\nTikTok: {total_tiktok}')
    else:
        await message.answer('У вас нет доступа к этой функции(', reply_markup=kb.call_menu)


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


    file_size = os.path.getsize(path_to_video)  
    max_size = 50 * 1024 * 1024  

    if file_size <= max_size:
        await message.answer_video(video=FSInputFile(path_to_video))
        await message.answer('**Вот и ваше видео!)** 🎬\n\nЧто-то еще? 💭', parse_mode="Markdown", reply_markup=kb.call_menu)

        config = configparser.ConfigParser()
        config.read('data.ini')

        subsection_value = config.get(f'{message.from_user.id}', 'youtube')
        current_value_int = int(subsection_value)
        new_value = current_value_int + 1

        config.set(f'{message.from_user.id}', 'youtube', str(new_value))

        with open('data.ini', 'w') as configfile:
            config.write(configfile)
    else:
        await message.answer("⚠️ **К сожалению, ваше видео превышает 50 МБ!**\n\n"
                     "📦 По системе Telegram мы не можем отправить файлы больше этого размера.\n\n"
                     "💡 Мы активно работаем над улучшениями и в будущем сможем отправлять файлы до 2 ГБ! 🚀\n"
                     "Благодарим за терпение! 🙏", parse_mode="Markdown", reply_markup=kb.call_menu)

    os.remove(path_to_video)


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

    file_size = os.path.getsize(path_to_audio) 
    max_size = 50 * 1024 * 1024  

    if file_size <= max_size:
        await message.answer_audio(audio=FSInputFile(path_to_audio))
        await message.answer('**Вот и ваше аудио!)** 🎬\n\nЧто-то еще? 💭', parse_mode="Markdown", reply_markup=kb.call_menu)

        config = configparser.ConfigParser()
        config.read('data.ini')

        subsection_value = config.get(f'{message.from_user.id}', 'youtube')
        current_value_int = int(subsection_value)
        new_value = current_value_int + 1

        config.set(f'{message.from_user.id}', 'youtube', str(new_value))

        with open('data.ini', 'w') as configfile:
            config.write(configfile)
    else:
        await message.answer("⚠️ **К сожалению, ваше аудио превышает 50 МБ!**\n\n"
                     "📦 По системе Telegram мы не можем отправить файлы больше этого размера.\n\n"
                     "💡 Мы активно работаем над улучшениями и в будущем сможем отправлять файлы до 2 ГБ! 🚀\n"
                     "Благодарим за терпение! 🙏", parse_mode="Markdown", reply_markup=kb.call_menu)
    
    os.remove(path_to_video)
    os.remove(path_to_audio)




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

    file_size = os.path.getsize(path_to_video)  
    max_size = 50 * 1024 * 1024  

    if file_size <= max_size:
        await message.answer_video(video=FSInputFile(path_to_video))
        await message.answer('**Вот и ваше видео!)** 🎬\n\nЧто-то еще? 💭', parse_mode="Markdown", reply_markup=kb.call_menu)

        config = configparser.ConfigParser()
        config.read('data.ini')

        subsection_value = config.get(f'{message.from_user.id}', 'tiktok')
        current_value_int = int(subsection_value)
        new_value = current_value_int + 1

        config.set(f'{message.from_user.id}', 'tiktok', str(new_value))

        with open('data.ini', 'w') as configfile:
            config.write(configfile)
    else:
        await message.answer("⚠️ **К сожалению, ваше видео превышает 50 МБ!**\n\n"
                     "📦 По системе Telegram мы не можем отправить файлы больше этого размера.\n\n"
                     "💡 Мы активно работаем над улучшениями и в будущем сможем отправлять файлы до 2 ГБ! 🚀\n"
                     "Благодарим за терпение! 🙏", parse_mode="Markdown", reply_markup=kb.call_menu)
    os.remove(path_to_video)

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

    file_size = os.path.getsize(path_to_audio) 
    max_size = 50 * 1024 * 1024  

    if file_size <= max_size:
        await message.answer_audio(audio=FSInputFile(path_to_audio))
        await message.answer('**Вот и ваше аудио!)** 🎬\n\nЧто-то еще? 💭', parse_mode="Markdown", reply_markup=kb.call_menu)

        config = configparser.ConfigParser()
        config.read('data.ini')

        subsection_value = config.get(f'{message.from_user.id}', 'tiktok')
        current_value_int = int(subsection_value)
        new_value = current_value_int + 1

        config.set(f'{message.from_user.id}', 'tiktok', str(new_value))

        with open('data.ini', 'w') as configfile:
            config.write(configfile)
    else:
        await message.answer("⚠️ **К сожалению, ваше аудио превышает 50 МБ!**\n\n"
                     "📦 По системе Telegram мы не можем отправить файлы больше этого размера.\n\n"
                     "💡 Мы активно работаем над улучшениями и в будущем сможем отправлять файлы до 2 ГБ! 🚀\n"
                     "Благодарим за терпение! 🙏", parse_mode="Markdown", reply_markup=kb.call_menu)
    os.remove(path_to_video)
    os.remove(path_to_audio)


# Instagram

# Обоботчик нажатия > Instagram
@router.callback_query(F.data == 'menu_instagram')
async def get_youtube_url(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Instagram.url)
    await callback.message.edit_text('💬 **Отправь ссылку на Сториз/Reels**', parse_mode="Markdown")

# Процесс загрузки > Instagram
@router.message(Instagram.url)
async def chek_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    data = await state.get_data()

    url = data["url"]

    await state.clear()

    await message.answer('🚀 **Уже скачиваю!** ⬇️', parse_mode="Markdown")

    path_to_video = await download_instagram_video(url)

    file_size = os.path.getsize(path_to_video)  
    max_size = 50 * 1024 * 1024  

    if file_size <= max_size:
        await message.answer_video(video=FSInputFile(path_to_video))
        await message.answer('**Вот и ваше видео!)** 🎬\n\nЧто-то еще? 💭', parse_mode="Markdown", reply_markup=kb.call_menu)

        config = configparser.ConfigParser()
        config.read('data.ini')

        subsection_value = config.get(f'{message.from_user.id}', 'instagram')
        current_value_int = int(subsection_value)
        new_value = current_value_int + 1

        config.set(f'{message.from_user.id}', 'instagram', str(new_value))

        with open('data.ini', 'w') as configfile:
            config.write(configfile)
    else:
        await message.answer("⚠️ **К сожалению, ваше видео превышает 50 МБ!**\n\n"
                     "📦 По системе Telegram мы не можем отправить файлы больше этого размера.\n\n"
                     "💡 Мы активно работаем над улучшениями и в будущем сможем отправлять файлы до 2 ГБ! 🚀\n"
                     "Благодарим за терпение! 🙏", parse_mode="Markdown", reply_markup=kb.call_menu)

    os.remove(path_to_video)


# Другое

# Показ статистики
@router.callback_query(F.data == 'my_statistics')
async def get_youtube_url(callback: CallbackQuery, state: FSMContext):

    config = configparser.ConfigParser()
    config.read('data.ini')

    current_value_tiktok = int(config.get(f'{callback.from_user.id}', 'tiktok'))
    current_value_youtube = int(config.get(f'{callback.from_user.id}', 'youtube'))
    current_value_instagram = int(config.get(f'{callback.from_user.id}', 'instagram'))

    full = current_value_tiktok + current_value_youtube + current_value_instagram

    await callback.message.edit_text(f'⚙️ **Ваша статистика:**\nВсего скачиваний: {full}\nTikTok: {current_value_tiktok}\nYouTube: {current_value_youtube}\nInstagram: {current_value_instagram}', parse_mode="Markdown", reply_markup=kb.call_menu)