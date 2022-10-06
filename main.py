import logging
import handlers
from logging.handlers import SocketHandler

import telegram.ext as tel
from sql_execute import SQLExecuter
import tel_consts as tc
from tel_answers_generator import answers_generator
import warnings
import json
from os.path import exists


# читаем настройки, если их нет - выходим
if not exists(tc.TEL_CONFIG):
    print('Настройки не найдены')
    exit()

with open(tc.TEL_CONFIG, 'r') as f:
    config = json.load(f)

# отключаю warning pandas
warnings.filterwarnings('ignore', 'pandas only support SQLAlchemy')

# лог
if 'file_log' in config.keys():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        filename=config['file_log'],
        filemode='w'
    )
else:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

logger = logging.getLogger()
socket_handler = SocketHandler("127.0.0.1", 19996)
logger.addHandler(socket_handler)

# подключение к базе генератора ответов
answers_generator.sql_executor = SQLExecuter(config['connect_string'])

# создание бота
application = tel.Application.builder().token(config['token']).build()

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

# Запуск бота
application.run_polling()
