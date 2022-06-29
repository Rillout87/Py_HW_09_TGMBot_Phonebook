from bot_token import tok
from controller import main_handler

import logging
import telebot
from typing import Dict
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
updater = Updater(tok)
dispatcher = updater.dispatcher

dispatcher.add_handler(main_handler)
    
updater.start_polling()
print('server started')
updater.idle()


# def message(update, context):
#     text = update.message.text
#     if text.lower() == 'привет':
#         context.bot.send_message(update.effective_chat.id, 'И тебе привет..')
#     else:
#         context.bot.send_message(update.effective_chat.id, 'я тебя не понимаю')


# def unknown(update, context):
#     context.bot.send_message(update.effective_chat.id, f'Шо сказал, не пойму')


# start_handler = CommandHandler('start', controller.menu)
# show_all_contacts_handler = CommandHandler('show_cont', controller.show_all_contacts)


# #info_handler = CommandHandler('info', info)
# message_handler = MessageHandler(Filters.text, message)
# unknown_handler = MessageHandler(Filters.command, unknown) #/game


# dispatcher.add_handler(start_handler)
# dispatcher.add_handler(show_all_contacts_handler)



# #dispatcher.add_handler(conv_handler)
# #dispatcher.add_handler(info_handler)
# dispatcher.add_handler(unknown_handler)
# dispatcher.add_handler(message_handler)

# print('server started')
# updater.start_polling()
# updater.idle()


