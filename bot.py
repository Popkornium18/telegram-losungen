"""A Telegram bot that can be queried for Losungen
and sends the daily Losung to subscribers
"""
import datetime
from time import sleep
import logging
import threading
from typing import Any, Coroutine, List
import schedule
from telebot.async_telebot import AsyncTeleBot
from telebot import logger as telebot_logger
from telebot.types import Message
from sqlalchemy.orm import Session
from config import cfg
from losungen import SessionMaker
from losungen.models import Subscriber, TagesLosung
from losungen.repositories import TagesLosungRepository, SubscriberRepository
from importer import import_year

if cfg["LOG"] == "systemd":
    from cysystemd.journal import JournaldLogHandler

    log_handler = JournaldLogHandler()
    log_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
else:
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(
        logging.Formatter("[%(name)s:%(asctime)s:%(levelname)s] %(message)s")
    )


bot = AsyncTeleBot(cfg["API_KEY"], parse_mode="MARKDOWN")

logger = logging.getLogger("telegram-losungen")
logger.addHandler(log_handler)
telebot_logger.handlers = []
telebot_logger.parent = logger
log_handler.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
telebot_logger.setLevel(logging.INFO)


@bot.message_handler(commands=["start", "Start", "hilfe", "Hilfe", "help", "Help"])
async def usage(message: Message) -> None:
    """Replies with usage information"""
    reply = """Dieser (inoffizielle) *Losungs-Bot* kann Dir täglich die Losung des Tages zuschicken.
Außerdem kannst Du die Losung eines bestimmten Tages abfragen.

*Benutzung*:
/abo - Die täglichen Losungen abonnieren
/deabo - Das tägliche Losungs-Abo beenden
/heute - Die heutige Losung abrufen
/datum - Die Losung eines bestimmten Datums abrufen
/hilfe - Diesen Hilfstext anzeigen

Den Quellcode dieses Bots findest Du auf [GitHub](https://github.com/Popkornium18/telegram-losungen).
"""
    await bot.send_message(message.chat.id, reply, disable_web_page_preview=True)


@bot.message_handler(commands=["heute", "Heute"])
async def send_losung(message: Message, date_query: datetime.date = None) -> None:
    """Sends a formatted Losung for a given date to the requesting chat.
    The date defaults to the current date.
    """
    date_query = datetime.date.today() if date_query is None else date_query
    logger.info("Requesting TagesLosung of %s", date_query)
    session: Session = SessionMaker()
    repo = TagesLosungRepository(session)
    losung = repo.get_by_date(date_query)
    session.close()
    if not losung:
        date_pretty = date_query.strftime("%d.%m.%Y")
        await bot.send_message(
            message.chat.id,
            f"Für das Datum *{date_pretty}* wurde leider keine Losung gefunden.",
        )
        logger.warning("No TagesLosung found for %s", date_query)
    else:
        reply = _format_tageslosung(losung)
        await bot.send_message(message.chat.id, reply, disable_web_page_preview=True)


@bot.message_handler(commands=["datum", "Datum"])
async def send_losung_date(message: Message) -> None:
    """Parses a date that is specified as a parameter to the command
    and calls `send_losung` with that date.
    """
    if not message.text:
        return
    request = message.text.split()
    if len(request) < 2:
        yesterday = (datetime.date.today() - datetime.timedelta(1)).strftime("%d.%m.%Y")
        await bot.send_message(message.chat.id, f"Benutzung: /datum {yesterday}")
        return

    try:
        date_query = datetime.datetime.strptime(request[1], "%d.%m.%Y").date()
        await send_losung(message, date_query)
    except ValueError:
        yesterday = (datetime.date.today() - datetime.timedelta(1)).strftime("%d.%m.%Y")
        await bot.send_message(
            message.chat.id,
            f"Das Datum hat nicht das richtige Format. Benutzung: /datum {yesterday}",
        )
        return


@bot.message_handler(commands=["abo", "Abo", "sub", "Sub"])
async def subscribe(message: Message) -> None:
    """Adds a chat to the subscriber list"""
    session: Session = SessionMaker()
    repo = SubscriberRepository(session)
    subscriber = repo.get_by_id(message.chat.id)
    if not subscriber:
        repo.add(Subscriber(chat_id=message.chat.id))
        session.commit()
        await bot.send_message(
            message.chat.id,
            "Du bekommst jetzt täglich die Losungen. Benutze /deabo zum Stoppen.",
        )
    else:
        await bot.send_message(
            message.chat.id,
            "Du hast die täglichen Losungen schon abonniert. Benutze /deabo zum Stoppen.",
        )
    session.close()


@bot.message_handler(commands=["deabo", "Deabo", "unsub", "Unsub"])
async def unsubscribe(message: Message) -> None:
    """Removes a chat from the subscriber list"""
    session: Session = SessionMaker()
    repo = SubscriberRepository(session)
    subscriber = repo.get_by_id(message.chat.id)
    if subscriber:
        repo.delete(subscriber)
        session.commit()
        await bot.send_message(
            message.chat.id,
            "Du bekommst jetzt keine täglichen Losungen mehr.",
        )
    else:
        await bot.send_message(
            message.chat.id,
            "Du hast die täglichen Losungen nicht abonniert. Benutze /abo zum abonnieren.",
        )
    session.close()


def _format_tageslosung(losung: TagesLosung) -> str:
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
    pretty_date: str = losung.date.strftime("*%d.%m.%Y*")
    losung_link: str = url_bibleserver + losung.losung_verse.replace(" ", "")
    lehrtext_link: str = url_bibleserver + losung.lehrtext_verse.replace(" ", "")
    losung_formatted: str = losung.losung.replace("/", "")
    lehrtext_formatted: str = losung.lehrtext.replace("/", "")
    if losung.special_date:
        pretty_date += f" ({losung.special_date})"

    reply = f"""{dow}, der {pretty_date}:\n
*Losung*: [{losung.losung_verse}]({losung_link})
_{losung_formatted}_\n
*Lehrtext*: [{losung.lehrtext_verse}]({lehrtext_link})
_{lehrtext_formatted}_"""
    return reply


async def _send_daily_losungen() -> None:
    """Triggers broadcasting of the daily Losung"""
    session: Session = SessionMaker()
    repo = TagesLosungRepository(session)
    losung = repo.get_by_date()
    session.close()
    if losung:
        message = _format_tageslosung(losung)
        await _broadcast(message)


async def _broadcast(message: str) -> None:
    """Broadcasts a message to all subscribers"""
    session: Session = SessionMaker()
    repo = SubscriberRepository(session)
    subscribers = repo.list()
    session.close()
    tasks: List[Coroutine[Any, Any, Message]] = []
    for subscriber in subscribers:
        tasks.append(
            bot.send_message(subscriber.chat_id, message, disable_web_page_preview=True)
        )

    for task in tasks:
        await task
    logger.info("Broadcast sent to %i subscribers", len(subscribers))


def _setup_schedule() -> None:
    """Sets up and runs recurring jobs"""
    schedule.every().day.at("08:00").do(_send_daily_losungen)
    schedule.every(1).week.do(import_year)
    while True:
        schedule.run_pending()
        sleep(1)


def main() -> None:
    import_year()
    thread_schedule = threading.Thread(target=_setup_schedule)
    thread_schedule.start()
    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()
