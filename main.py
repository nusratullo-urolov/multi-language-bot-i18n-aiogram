import os
from pathlib import Path
from typing import Tuple, Any

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv

load_dotenv('.env')
from language import languages

TOKEN = os.getenv('TOKEN')
I18N_DOMAIN = "mybot"

BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / "locales"

bot = Bot(TOKEN)
dp = Dispatcher(bot)

LANG_STORAGE = {}
LANGS = ["O'zbek 🇺🇿", "English 🇺🇸", "Pусский 🇷🇺"]


class Localization(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> str:
        user: types.User = types.User.get_current()


        if LANG_STORAGE.get(user.id) is None:
            LANG_STORAGE[user.id] = "O'zbek 🇺🇿"
        *_, data = args
        language = data['locale'] = LANG_STORAGE[user.id]
        return language


i18n = Localization(I18N_DOMAIN, LOCALES_DIR)
dp.middleware.setup(i18n)

_ = i18n.lazy_gettext

rkm = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
rkm.add("O'zbek 🇺🇿").add('Pусский 🇷🇺').add('English 🇺🇸')


def find_language(languages, locale):
    language_codes = [list(lang.keys())[0] for lang in languages]
    # print(locale)
    if locale in language_codes:
        return language_codes.index(locale)


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer('Tilni tanlang', reply_markup=rkm)
    user: types.User = types.User.get_current()
    print(LANG_STORAGE.get(user.id))


@dp.message_handler(lambda message: message.text in ["O'zbek 🇺🇿", 'Pусский 🇷🇺', 'English 🇺🇸'])
async def choose_language(message: types.Message, locale):
    lang = message.text
    if not lang:
        return await message.answer(_("Specify your language.\nExample: /setlang en"))
    if lang not in LANGS:
        return await message.answer(_("This language is not available. Use en or ru"))
    locale = lang
    LANG_STORAGE[message.from_user.id] = lang

    await message.answer(languages[find_language(languages, locale)][locale]['start'])


@dp.message_handler(lambda message: message.text == 'hello')
async def hello(message: types.Message, locale):
    await message.answer(
        f"{languages[find_language(languages, locale)][locale]['hello']}" + ' ' + message.from_user.username)


@dp.message_handler(commands="lang")
async def cmd_lang(message: types.Message, locale):
    await message.answer(
        _("Your current language: {language}").format(language=locale)
    )


executor.start_polling(dp)
