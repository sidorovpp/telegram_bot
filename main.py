import logging
import handlers
from logging.handlers import SocketHandler
import telegram.ext as tel
from sql_execute import SQLExecuter
import tel_consts as tc
from generators.tel_answers_generator import answers_generator
import warnings
import json
from os.path import exists, abspath, dirname
from os import chdir
import traceback
import asyncio
import sys
from tendo import singleton
from telegram.warnings import PTBUserWarning
import conversation
from generators.tel_accounts import AccountsGenerator
from generators.tel_tasks import TasksGenerator
from generators.tel_coordinations import CoordinationsGenerator
from generators.tel_petitions import PetitionsGenerator
from generators.tel_documents import DocumentsGenerator
from generators.tel_clients import ClientsGenerator
from generators.tel_common import CommonGenerator
from generators.tel_show_sheets import ShowSheetsGenerator
from generators.tel_specifications import SpecificationsGenerator


def start():
    # проверка двойного запуска
    try:
        singleton.SingleInstance()
    except (Exception,):
        sys.exit()

    # устанавливаем текущую папку файла
    chdir(dirname((abspath(__file__))))
    # читаем настройки, если их нет - выходим
    if not exists(tc.TEL_CONFIG):
        print('Настройки не найдены')
        exit()

    with open(tc.TEL_CONFIG, 'r') as f:
        config = json.load(f)

    # отключаю warning
    warnings.filterwarnings(action='ignore', message='pandas only supports')
    warnings.filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
    level = logging.INFO
    if 'level' in config.keys():
        level = config['level']

    # лог
    if 'file_log' in config.keys():
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=level,
            filename=config['file_log'],
            filemode='w'
        )
    else:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=level
        )

    logger = logging.getLogger()
    socket_handler = SocketHandler("127.0.0.1", 19996)
    logger.addHandler(socket_handler)

    try:
        # подключение к базе генератора ответов
        answers_generator.sql_executor = SQLExecuter(
            config['server'],
            config['database'],
            config['user'],
            config['password'],
        )

        # регистрируем кастомные генераторы ответов
        # для общих методов
        answers_generator.add_custom_generator(CommonGenerator)
        # для счетов
        answers_generator.add_custom_generator(AccountsGenerator)
        # для задач
        answers_generator.add_custom_generator(TasksGenerator)
        # для согласования
        answers_generator.add_custom_generator(CoordinationsGenerator)
        # для заявок
        answers_generator.add_custom_generator(PetitionsGenerator)
        # для документов
        answers_generator.add_custom_generator(DocumentsGenerator)
        # для клиентов
        answers_generator.add_custom_generator(ClientsGenerator)
        # для смотровых листов
        answers_generator.add_custom_generator(ShowSheetsGenerator)
        # спецификации
        answers_generator.add_custom_generator(SpecificationsGenerator)

        # создание бота
        application = tel.Application.builder().token(config['token']).build()

        # обработка Conversation
        h = conversation.TaskHandler()
        application.add_handler(h.conv_handler)
        h = conversation.SMSHandler()
        application.add_handler(h.conv_handler)
        h = conversation.NoteHandler()
        application.add_handler(h.conv_handler)
        h = conversation.INNHandler()
        application.add_handler(h.conv_handler)

        # Регистрация обработчика на текстовые сообщения, но не команды
        application.add_handler(tel.MessageHandler(tel.filters.TEXT & ~tel.filters.COMMAND, handlers.text_handler))
        # Регистрация обработчика на документы
        application.add_handler(tel.MessageHandler(tel.filters.Document.ALL | tel.filters.PHOTO,
                                                   handlers.document_handler))

        # Регистрация обработчиков
        application.add_handler(tel.CommandHandler(tc.TEL_START, callback=handlers.start))
        application.add_handler(tel.CommandHandler(tc.TEL_HELP, callback=handlers.print_help))
        application.add_handler(tel.CallbackQueryHandler(handlers.query_handler))
        # application.add_handler(tel.CommandHandler(tc.TEL_NOTIFICATIONS, callback=handlers.notifications))

        # в тестовой версии убираю рассылки
        if config['database'].lower() != 'vkb_test1':
            handlers.start_jobs(application.job_queue)

        return application
    except (Exception,):
        logging.error(traceback.format_exc())


# запуск не из сервиса
def run_polling(application):
    # Запуск бота
    try:
        application.run_polling()
    except (Exception,):
        logging.error(traceback.format_exc())


# запуск из сервиса, написал свой цикл, run_polling не работает
async def run_cycle(application):
    # Запуск бота
    try:
        await application.initialize()
        await application.start()
        last_update_id = 0
        while True:
            updates = await application.bot.get_updates(
                last_update_id,
                timeout=10,
                allowed_updates=None)
            if updates:
                for update in updates:
                    await application.update_queue.put(update)
                last_update_id = updates[-1].update_id + 1

            await asyncio.sleep(1)
    except (Exception,):
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    app = start()
    run_polling(app)
    # asyncio.run(run_cycle(app))
