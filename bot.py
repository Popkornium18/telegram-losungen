"""A Telegram bot that can be queried for Losungen
and sends the daily Losung to subscribers
"""
import datetime
from time import sleep
import logging
import threading
import schedule
import telebot
from config import cfg
from losungen import Session
from losungen.models import TagesLosung, JahresLosung, Subscriber
from importer import import_year

bot = telebot.AsyncTeleBot(cfg["API_KEY"], parse_mode="MARKDOWN")
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


@bot.message_handler(commands=["heute", "Heute"])
def send_losung(message, date_query=datetime.date.today()):
    """Sends a formatted Losung for a given date to the requesting chat.
    The date defaults to the current date.
    """
    losung = _get_losung(date_query)
    if not losung:
        date_pretty = date_query.strftime("%d.%m.%Y")
        task = bot.send_message(
            message.chat.id,
            f"Für das Datum *{date_pretty}* wurde leider keine Losung gefunden.",
        )
    else:
        reply = _format_losung(losung)
        task = bot.send_message(message.chat.id, reply, disable_web_page_preview=True)
    task.wait()


@bot.message_handler(commands=["datum", "Datum"])
def send_losung_date(message):
    """Parses a date that is specified as a parameter to the command
    and calls `send_losung` with that date.
    """
    request = message.text.split()
    if len(request) < 2:
        yesterday = (datetime.date.today() - datetime.timedelta(1)).strftime("%d.%m.%Y")
        task = bot.send_message(message.chat.id, f"Benutzung: /datum {yesterday}")
        task.wait()
        return

    try:
        date_query = datetime.datetime.strptime(request[1], "%d.%m.%Y").date()
        send_losung(message, date_query)
    except ValueError:
        yesterday = (datetime.date.today() - datetime.timedelta(1)).strftime("%d.%m.%Y")
        task = bot.send_message(
            message.chat.id,
            f"Das Datum hat nicht das richtige Format. Benutzung: /datum {yesterday}",
        )
        task.wait()
        return


@bot.message_handler(commands=["abo", "Abo", "sub", "Sub"])
def subscribe(message):
    """Adds a chat to the subscriber list"""
    session = Session()
    subscriber = session.query(Subscriber).get(message.chat.id)
    if not subscriber:
        subscriber = Subscriber(chat_id=message.chat.id)
        session.add(subscriber)
        session.commit()
        task = bot.send_message(
            message.chat.id,
            "Du bekommst jetzt täglich die Losungen. Benutze /deabo zum Stoppen.",
        )
    else:
        task = bot.send_message(
            message.chat.id,
            "Du hast die täglichen Losungen schon abonniert. Benutze /deabo zum Stoppen.",
        )

    task.wait()
    session.close()


@bot.message_handler(commands=["deabo", "Deabo", "unsub", "Unsub"])
def unsubscribe(message):
    """Removes a chat from the subscriber list"""
    session = Session()
    subscriber = session.query(Subscriber).get(message.chat.id)
    if subscriber:
        session.delete(subscriber)
        session.commit()
        task = bot.send_message(
            message.chat.id,
            "Du bekommst jetzt keine täglichen Losungen mehr.",
        )
    else:
        task = bot.send_message(
            message.chat.id,
            "Du hast die täglichen Losungen nicht abonniert. Benutze /abo zum abonnieren.",
        )
    task.wait()
    session.close()


def _get_losung(date_query=datetime.date.today()):
    """Retrieves a TagesLosung object from the database for
    a given date. The date defaults to the current date.
    """
    session = Session()
    losung = session.query(TagesLosung).get(date_query)
    session.close()
    return losung


def _format_losung(losung):
    """Formats a given Losung as a Markdown message"""
    url_bibleserver = "https://www.bibleserver.com/LUT/"
    days = [
        "Montag",
        "Dienstag",
        "Mittwoch",
        "Donnerstag",
        "Freitag",
        "Samstag",
        "Sonntag",
    ]
    dow = days[losung.day_of_week]
    pretty_date = losung.date.strftime("*%d.%m.%Y*")
    losung_link = url_bibleserver + losung.losung_verse.replace(" ", "")
    lehrtext_link = url_bibleserver + losung.lehrtext_verse.replace(" ", "")
    losung_formatted = losung.losung.replace("/", "")
    lehrtext_formatted = losung.lehrtext.replace("/", "")
    if losung.special_date:
        pretty_date += f" ({losung.special_date})"

    reply = f"""{dow}, der {pretty_date}:\n
*Losung*: [{losung.losung_verse}]({losung_link})
_{losung_formatted}_\n
*Lehrtext*: [{losung.lehrtext_verse}]({lehrtext_link})
_{lehrtext_formatted}_"""
    return reply


def _send_daily_losungen():
    """Triggers broadcasting of the daily Losung"""
    losung = _get_losung()
    if losung:
        message = _format_losung(losung)
        _broadcast(message)


def _broadcast(message):
    """Broadcasts a message to all subscribers"""
    session = Session()
    tasks = []
    subscribers = session.query(Subscriber).all()
    for subscriber in subscribers:
        tasks.append(
            bot.send_message(subscriber.chat_id, message, disable_web_page_preview=True)
        )

    for task in tasks:
        task.wait()
    session.close()


def _setup_schedule():
    """Sets up and runs recurring jobs"""
    schedule.every().day.at("08:00").do(_send_daily_losungen)
    schedule.every(1).week.do(import_year)
    while True:
        schedule.run_pending()
        sleep(1)


import_year()
thread_schedule = threading.Thread(target=_setup_schedule)
thread_schedule.start()
bot.polling()
