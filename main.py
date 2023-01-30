import logging
import handlers
from logging.handlers import SocketHandler
import telegram.ext as tel
from sql_execute import SQLExecuter
import tel_consts as tc
from tel_answers_generator import answers_generator
import warnings
import json
from os.path import exists, abspath, dirname
from os import chdir
import traceback
import asyncio
import sys
from tendo import singleton


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

    # отключаю warning pandas
    warnings.filterwarnings('ignore', 'pandas only supports')
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
        answers_generator.sql_executor = SQLExecuter(config['connect_string'])

        # создание бота
        application = tel.Application.builder().token(config['token']).build()

        # обработка Conversation
        th = handlers.TaskHandler()
        application.add_handler(th.conv_handler)

        # Регистрация обработчика на текстовые сообщения, но не команды
        application.add_handler(tel.MessageHandler(tel.filters.TEXT & ~tel.filters.COMMAND, handlers.text_handler))
        # Регистрация обработчика на документы
        application.add_handler(tel.MessageHandler(tel.filters.Document.ALL | tel.filters.PHOTO,
                                                   handlers.document_handler))

        # Регистрация обработчиков
        application.add_handler(tel.CommandHandler(tc.TEL_START, callback=handlers.start))
        application.add_handler(tel.CommandHandler(tc.TEL_HELP, callback=handlers.print_help))
        application.add_handler(tel.CallbackQueryHandler(handlers.query_handler))
        application.add_handler(tel.CommandHandler(tc.TEL_NOTIFICATIONS, callback=handlers.notifications))

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
async def run_cicle(application):
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
    # asyncio.run(run_cicle(app))
