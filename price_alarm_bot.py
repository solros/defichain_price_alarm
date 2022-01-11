#!/usr/bin/env python

import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from price_alarm import *
import price_alarm_secrets

def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Hi! Use /subscribe to subscribe to price alarms (example "/subscribe DFI < 2.2").')


def show_current_values(update: Update, context: CallbackContext) -> None:
    data = get_bot_data()
    update.message.reply_text(data)


def subscribe(update: Update, context: CallbackContext) -> None:
    try:
        chat_id = update.message.chat_id
        if not context.args:
            raise
        if add_subscription(chat_id, "".join(context.args)):
            logger.info(f"New subscription: {chat_id}, {''.join(context.args)}")
            update.message.reply_text("Subscribed! Use /unsubscribe if you change your mind. (This will remove all of your alarms.)")
        else:
            raise
    except Exception as e:
        logger.warning(e)
        update.message.reply_text("Usage: \"/subscribe {token} </> {value}\", example: \"/subscribe DUSD < 1.1\"")


def unsubscribe(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    logger.info(f"Unsubscribing {chat_id}")
    text = 'Unsubscribed!' if remove_subscriptions(chat_id) else 'You have no active subscriptions.'
    update.message.reply_text(text)


def list_subscriptions(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    text = get_subscriptions(chat_id)
    update.message.reply_text(text)



def add_subscription(chatid: str, query: str) -> bool:
    chatid = str(chatid)
    try:
        data = read_data()
        subscriptions = data.get(chatid, [])
        subscriptions.append(query)
        data[chatid] = subscriptions
        write_data(data)
        return True
    except:
        return False

def remove_subscriptions(chatid: str) -> bool:
    chatid = str(chatid)
    try:
        data = read_data()
        if chatid in data:
            data.pop(chatid)
            write_data(data)
            return True
        else:
            return False
    except:
        return False

def get_subscriptions(chatid: str) -> str:
    chatid = str(chatid)
    try:
        data = read_data()
        return repr(data.get(chatid, []))
    except:
        return ""


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(price_alarm_secrets.telegram_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("show", show_current_values))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dispatcher.add_handler(CommandHandler("list", list_subscriptions))


    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
