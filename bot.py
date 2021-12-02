from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random
from config import TOKEN
import db

quote_bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(quote_bot, storage=storage)
scheduler = AsyncIOScheduler()


async def send_quote() -> None:
    """
    Calls database function to get all users that were added to the database already.
    For each user_id gets last quote that was sent to this user,
    then gets a random number between 1 and total number of quotes.
    If last sent quote is the same as chosen, uses next to it quote instead.
    Sends quote to user (or chat) and then updates 'last_quote' field of User table.
    """
    for user in db.get_user_ids():
        last_quote = db.get_last_quote(user)
        quote_id = random.randint(1, db.get_number_of_quotes())
        if last_quote == quote_id:
            quote_id += 1
        message = db.get_quote_by_id(quote_id)
        await dp.bot.send_message(user, message)
        db.update_last_quote(quote_id, user)


def schedule_jobs() -> None:
    """
    Collects send_quote into scheduler that will call send_quote() every period of time. Open
    AsyncIOScheduler.add_job documentation to learn more about configuring this period of time. It's pretty flexible.
    Here it is set on every day at 12:30 server time.
    """
    scheduler.add_job(send_quote, 'cron', hour=7, minute=30)


async def on_startup(dp: Dispatcher) -> None:
    """
    This function will be used to tell our executor what to do on startup.
    You can also put all type of logger initializers etc here.
    """
    schedule_jobs()


@dp.message_handler(commands=['Song', 'song'])
async def send_song_name(message: types.Message) -> None:
    """
    Uses id found in message dict to call database and find the name of the song which was last sent to user or chat.
    If database returns TypeError it most of the times mean that last_quote field for this id is None,
    meaning that id never received quotes before. Thus it sends some plug-message you can choose on your own.
    If func can't find chat.id and sends AttributeError, we proceed to look for user id.
    Nested tries are necessary until I find another way to work around the fact that bot
    can be used in both groups and userchats with similar functionality.
    """
    try:
        songname = db.get_song_name(message.chat.id)
        await quote_bot.send_message(message.chat.id, songname)
    except TypeError:
        await quote_bot.send_message(message.chat.id,
                                     '''Шило для тебя еще не пел. Он зачитывает свои
                                      строки каждый день около 12''')
    except AttributeError:
        try:
            songname = db.get_song_name(message.from_user.id)
            await quote_bot.send_message(message.from_user.id, songname)
        except TypeError:
            await quote_bot.send_message(message.chat.id,
                                         '''Шило для тебя еще не пел. Он зачитывает свои
                                                  строки каждый день около 12''')
        except AttributeError:
            pass


@dp.message_handler(commands=['Link', 'link', 'youtube', 'Youtube', 'YouTube'])
async def send_song_link(message):
    """
    Uses id found in message dict to call database and find YouTube link to the song which was last sent to user or
    chat. If database returns TypeError it most of the times mean that last_quote field for this id is None,
    meaning that id never received quotes before. Thus it sends some plug-message you can choose on your own. If func
    can't find chat.id and sends AttributeError, we proceed to look for user id. Nested tries are necessary until I
    find another way to work around the fact that bot can be used in both groups and userchats with similar
    functionality.
    """
    try:
        songlink = db.get_song_link(message.chat.id)
        await quote_bot.send_message(message.chat.id, songlink)
    except TypeError:
        await quote_bot.send_message(message.chat.id,
                                     '''Шило для тебя еще не пел. Он зачитывает свои
                                              строки каждый день около 12''')
    except AttributeError:
        try:
            songlink = db.get_song_link(message.from_user.id)
            await quote_bot.send_message(message.from_user.id, songlink)
        except TypeError:
            await quote_bot.send_message(message.chat.id,
                                         '''Шило для тебя еще не пел. Он зачитывает свои
                                                  строки каждый день около 12''')
        except AttributeError:
            pass


@dp.message_handler(commands=['register', 'Register'])
async def handle_new_users(message):
    """
    Handles /register message from group or user.
    After getting a new message from user or from group bot will try to add received id to database.
    If there is no chat id it will try to extract user id. If user already exists in table,
    it will send TypeError, thus passing and doing nothing.
    """
    try:
        db.add_user(message.chat.id)
        await quote_bot.send_message(message.chat.id, """Билет на концерт 'Кровостока' успешно куплен. 
        Встречаемся каждый день здесь в 12:30.""")
    except TypeError:
        pass
    except AttributeError:
        try:
            db.add_user(message.from_user.id)
            await quote_bot.send_message(message.from_user.id, """Билет на концерт 'Кровостока' успешно куплен. 
                    Встречаемся каждый день здесь в 12:30.""")
        except (TypeError, AttributeError):
            pass


@dp.message_handler(commands=['help', 'Help'])
async def handle_new_users(message):
    """
    Handles /help message providing info on how to use this bot.
    Similar to other message handlers.
    """
    try:
        await quote_bot.send_message(message.chat.id, """Эй, тупо запомните эти простые команды:\n
        /register поможет купить билеты на концерт 'Кровостока'\n
        /song — и я скажу название песни, из которой взята последняя цитата\n
        /link — и я пришлю ссылку на последнюю песню""")
    except AttributeError:
        try:
            await quote_bot.send_message(message.from_user.id, """Эй, тупо запомните эти простые команды:\n
        /register поможет купить билеты на концерт 'Кровостока'\n
        /song — и я скажу название песни, из которой взята последняя цитата\n
        /link — и я пришлю ссылку на последнюю песню""")
        except AttributeError:
            pass


scheduler.start()
executor.start_polling(dp, on_startup=on_startup)
