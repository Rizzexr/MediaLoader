from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


call_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❤️ YouTube', callback_data='menu_youtube'),
     InlineKeyboardButton(text='🖤 TikTok', callback_data='menu_tiktok')],
    [InlineKeyboardButton(text='🧡 Instagram', callback_data='menu_instagram')],
    [InlineKeyboardButton(text='❓ Как это работает', url='https://telegra.ph/Skachat-TikTok--YouTube-11-16')],
    [InlineKeyboardButton(text='⚙️ Моя статистика', callback_data='my_statistics')]
])

call_menu_youtube = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎥 Скачать видео', callback_data='menu_youtube_video')],
    [InlineKeyboardButton(text='🎤 Скачать аудио', callback_data='menu_youtube_audio')]
])

call_menu_tiktok = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎥 Скачать видео', callback_data='menu_tiktok_video')],
    [InlineKeyboardButton(text='🎤 Скачать аудио', callback_data='menu_tiktok_audio')]
])