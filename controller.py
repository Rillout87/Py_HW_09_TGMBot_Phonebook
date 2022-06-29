import interface
import database_module
import import_from_file
import logger
import export_to_file
import telebot
import requests
from bot_token import tok

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove, bot
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

CHOOSING, SEARCHING, ADD_CONTACT, CHANGE_CONTACT, IMPORT_FILES = range(5)

main_keyboard = [
    ['Список контактов', 'Поиск контакта'],
    ['Добавить контакт', 'Изменить контакт'],
    ['Импорт контактов', 'Экспорт контактов'],
    ['Завершить']
]

back_to_main_menu_keyboard= [
    ['Вернуться в главное меню'] #огромную кнопка как изменить??
]

markup_main_menu = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=True, resize_keyboard=True)
markup_back_to_main_menu = ReplyKeyboardMarkup(back_to_main_menu_keyboard, one_time_keyboard=True, resize_keyboard=True)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Вас приветствует Телефонный справочник v2.0",
        reply_markup=markup_main_menu,
    )

    return CHOOSING

def back_to_main_menu(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Вы прервали операцию',
        reply_markup=markup_main_menu)
    return CHOOSING

def show_all_contacts (update: Update, context: CallbackContext) -> int:
    data = database_module.get_all_contacts()
    contact_list = interface.show_contacts(data)
    update.message.reply_text(
        contact_list,
        reply_markup=markup_main_menu
    )

    return CHOOSING

def contact_search_run (update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Введите данные для поиска',
        reply_markup=markup_back_to_main_menu
    )
    
    return SEARCHING

def contact_search (update: Update, context: CallbackContext) -> int:
    user_search = update.message.text
    data = database_module.get_contact_info(user_search)
    search_result = interface.show_contacts(data)
    update.message.reply_text(
        search_result,
        reply_markup=markup_main_menu
    )

    return CHOOSING

def add_contact (update: Update, context: CallbackContext) -> int:
    last_input = update.message.text
    user_data = context.user_data
    
    if last_input == 'Добавить контакт':
        update.message.reply_text('Добавление контакта') 
        update.message.reply_text('Введите фамилию:',
            reply_markup=markup_back_to_main_menu)
        user_data.clear()
        return ADD_CONTACT

    else:
        if len(user_data) == 0:
            user_data['surname'] = last_input
            update.message.reply_text('Введите имя:',
                reply_markup=markup_back_to_main_menu)
            return ADD_CONTACT
        
        elif len(user_data) == 1:
            user_data['name'] = last_input
            update.message.reply_text('Введите номер телефона:',
                reply_markup=markup_back_to_main_menu)
            return ADD_CONTACT

        elif len(user_data) == 2:
            user_data['phone'] = last_input
            update.message.reply_text('Введите комментарий:',
                reply_markup=markup_back_to_main_menu)
            return ADD_CONTACT

        elif len(user_data) == 3:
            user_data['comment'] = last_input
            database_module.add_contacts([user_data,])
            logger.add([user_data,], 'added')        # в логгере contact_id в конце встает  
            user_data.clear()
            update.message.reply_text('Контакт добавлен!',
                        reply_markup=markup_main_menu)
            return CHOOSING
        
def change_contact (update: Update, context: CallbackContext) -> int: # !!!вопрос: у нас есть проверка на то, если пользователь ничего не ввел?
    last_input = update.message.text                                   # + добавить удаление контакта!!
    user_data = context.user_data
    
    if last_input == 'Изменить контакт':
        update.message.reply_text('Изменение контакта') 
        update.message.reply_text('Выберите контакт для внесения изменений:')
        
        data = database_module.get_all_contacts()
        contact_list = interface.show_contacts(data)
        update.message.reply_text(
            contact_list,
            reply_markup=markup_back_to_main_menu
        )
        
        user_data.clear()
        return CHANGE_CONTACT
    
    else:
        if len(user_data) == 0:
            data = database_module.get_all_contacts()
            if len(data) < int(last_input):
                update.message.reply_text('В шары долбишся??\nТакого контакта нет!',
                reply_markup=markup_main_menu)
                return CHOOSING

            user_data['contact_id'] = int(last_input)
            update.message.reply_text('Введите новое имя:',
                reply_markup=markup_back_to_main_menu)
            return CHANGE_CONTACT
        
        elif len(user_data) == 1:
            user_data['surname'] = last_input
            update.message.reply_text('Введите новую фамилию:',
                reply_markup=markup_back_to_main_menu)
            return CHANGE_CONTACT        
        
        elif len(user_data) == 2:
            user_data['name'] = last_input
            update.message.reply_text('Введите новый номер телефона:',
                reply_markup=markup_back_to_main_menu)
            return CHANGE_CONTACT

        elif len(user_data) == 3:
            user_data['phone'] = last_input
            update.message.reply_text('Введите новый комментарий:',
                reply_markup=markup_back_to_main_menu)
            return CHANGE_CONTACT

        elif len(user_data) == 4:
            user_data['comment'] = last_input
            database_module.change_contact(user_data)
            logger.add(user_data, 'changed')          
            user_data.clear()
            update.message.reply_text('Контакт изменен!',
                        reply_markup=markup_main_menu)
            return CHOOSING


def import_contacts (update: Update, context: CallbackContext) -> int:
    last_input = update.message.text
    
    if last_input == 'Импорт контактов':        
        update.message.reply_text(
            'Загрузите файл необходимого формата с расширением ".csv" или ".json"',
            reply_markup=markup_back_to_main_menu
        )
        return IMPORT_FILES
    
    file_name = update.message.document.file_name
    file = context.bot.getFile(update.message.document.file_id)
    if file_name.split('.')[-1] == 'csv': # сюда еще можно будет добавить блок try except для проверки содержимого файла
        data = import_from_file.import_csv(file.download('./import_phonebook.csv'))
        database_module.add_contacts(data)
        logger.add(data, 'imported')
        
    elif file_name.split('.')[-1] == 'json':
        file.download('./import_phonebook.json')
        data = import_from_file.import_json(file.download('./import_phonebook.json'))
        database_module.add_contacts(data)
        logger.add(data, 'imported')

    else:
        update.message.reply_text('Файл не импортирован: неизвестное расширение',
                                    reply_markup=markup_main_menu)
        return CHOOSING
    
    update.message.reply_text('Контакты импортированы',reply_markup=markup_main_menu)
    return CHOOSING

def export_contacts (update: Update, context: CallbackContext) -> int:
    chat_id=update.message.chat.id
    file_csv = export_to_file.export_csv()
    context.bot.send_document(chat_id=chat_id, document=open(file_csv, 'rb'))       
    update.message.reply_text('Контакты успешно экпортированы',reply_markup=markup_main_menu)
    return CHOOSING

def done(update: Update, context: CallbackContext) -> int:

    update.message.reply_text(
        'Работа завершена!\n'
        'Для возврата запустите справочник командой /start',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


main_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('^Список контактов$'), show_all_contacts),
                MessageHandler(Filters.regex('^Поиск контакта$'), contact_search_run),
                MessageHandler(Filters.regex('^Добавить контакт$'), add_contact),
                MessageHandler(Filters.regex('^Изменить контакт$'), change_contact),
                MessageHandler(Filters.regex('^Импорт контактов$'), import_contacts),
                MessageHandler(Filters.regex('^Экспорт контактов$'), export_contacts)
            ],
            SEARCHING: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Вернуться в главное меню$')), contact_search),
                MessageHandler(Filters.regex('^Вернуться в главное меню$'), back_to_main_menu)
                
            ],
            ADD_CONTACT: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Вернуться в главное меню$')), add_contact),
                MessageHandler(Filters.regex('^Вернуться в главное меню$'), back_to_main_menu)
            ],
            CHANGE_CONTACT: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Вернуться в главное меню$')), change_contact),
                MessageHandler(Filters.regex('^Вернуться в главное меню$'), back_to_main_menu)
            ],
            IMPORT_FILES: [
                MessageHandler(Filters.document, import_contacts),
                MessageHandler(Filters.regex('^Вернуться в главное меню$'), back_to_main_menu)
            ]

        },
        fallbacks=[MessageHandler(Filters.regex('^Завершить$'), done)],
    )
