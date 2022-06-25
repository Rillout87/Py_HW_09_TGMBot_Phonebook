import interface
import database_module
import logger
import import_from_file as iff
import export_to_file

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

CHOOSING, SEARCHING, ADD_CONTACT, CHANGE_CONTACT = range(4)

main_keyboard = [
    ['Список контактов', 'Поиск контакта'],
    ['Добавить контакт', 'Изменить контакт'],
    ['Импорт контактов', 'Экспорт контактов'],
    ['Завершить']
]

back_to_main_menu_keyboard= [
    ['Вернуться в главное меню'] #огромную кнопка как изменить??
]

markup_main_menu = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=True)
markup_back_to_main_menu = ReplyKeyboardMarkup(back_to_main_menu_keyboard, one_time_keyboard=True)

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


def function_in_development (update: Update, context: CallbackContext) -> int:

    update.message.reply_text(
        'Не знаю как работать с файлами в боте\n'
        'Разберитесь по-братски, а?',
        reply_markup=markup_main_menu
    )

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
                MessageHandler(
                    Filters.regex('^Список контактов$'), show_all_contacts),
                MessageHandler(Filters.regex('^Поиск контакта$'), contact_search_run),
                MessageHandler(Filters.regex('^Добавить контакт$'), add_contact),
                MessageHandler(Filters.regex('^Изменить контакт$'), change_contact),
                MessageHandler(Filters.regex('^Импорт контактов$'), function_in_development),
                MessageHandler(Filters.regex('^Экспорт контактов$'), function_in_development)
            ],
            SEARCHING: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Вернуться в главное меню$')), contact_search
                ),
                MessageHandler(Filters.regex('^Вернуться в главное меню$'), back_to_main_menu)
                
            ],
            ADD_CONTACT: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Вернуться в главное меню$')),
                    add_contact,
                ),
                MessageHandler(Filters.regex('^Вернуться в главное меню$'), back_to_main_menu)
            ],
            CHANGE_CONTACT: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Вернуться в главное меню$')),
                    change_contact,
                ),
                MessageHandler(Filters.regex('^Вернуться в главное меню$'), back_to_main_menu)
            ],

        },
        fallbacks=[MessageHandler(Filters.regex('^Завершить$'), done)],
    )
















def menu(update, context):
    context.bot.send_message(update.effective_chat.id, interface.main_menu)
    #interface.start_page() #выпилить из функции ввод выбора меню и return


def show_all_contacts (update, context):
    data = database_module.get_all_contacts()
    contact_list = interface.show_contacts(data)
    context.bot.send_message(update.effective_chat.id, contact_list)
    




def run():
    
    while True:
    
        command = interface.start_page() 

        match command:
            case '1':     # Список всех контактов
                data = database_module.get_all_contacts()
                interface.show_contacts(data)

            case '2': # Поиск контакта
                user_search = interface.search_contact()
                data = database_module.get_contact_info(user_search)
                interface.show_contacts(data)
            
            
            case '3': # Добавить контакт

                new_contact = interface.add_contact()
                database_module.add_contacts(new_contact)
                logger.add(new_contact, 'added')
                interface.done_message()

            case '4': # Изменить дело
                data = database_module.get_all_contacts()
                interface.show_contacts(data)
                deal_id = interface.change_contact()
                one_contact = database_module.get_one_contact(deal_id)
                changed_contact = interface.change_contact_content(one_contact)
                if changed_contact['comment'] == 'Я что-то нажал и всё сломалось':
                    database_module.delete_contact(changed_contact['contact_id'])
                    logger.add(changed_contact, 'deleted')
                else:
                    database_module.change_contact(changed_contact)
                    logger.add(changed_contact, 'changed')
            
            case '5': # Импорт
                user_choice = interface.import_contacts()
                if user_choice == 'csv':
                    data = iff.import_csv('import_phonebook.csv')
                    database_module.add_contacts(data)
                    interface.result_mess(True)
                    logger.add(data, 'imported')
                elif user_choice == 'json':
                    data = iff.import_json('import_phonebook.json')
                    database_module.add_contacts(data)
                    interface.result_mess(True)
                    logger.add(data, 'imported')
                else:
                    interface.error_input()
                
                
            
            case '6': # Экспорт
                export_to_file.export_csv()
                # user_choice = interface.export_contacts()
                # if user_choice == 'csv':
                #     data = export_to_file.export_csv()

                #     interface.result_mess(True)
                #     #logger.add(data, 'exported')
                # elif user_choice == 'json':
                #     #data = export_to_file.export_json()
                    
                #     interface.result_mess(False)
                #     #logger.add(data, 'exported')
                # else:
                #     interface.error_input()

            case '7': # Выход
                interface.bye_mess()
                break
            
            case _:
                interface.error_input()


def change_action(user_answer: dict):
    match user_answer['user_choise']:
        case 1: # завершить дело
            return
        
        case 2: # изменить дело
            return

        case 3: # удалить дело
            return
