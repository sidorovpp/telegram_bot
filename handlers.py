import logging
import traceback
from telegram import Update, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.constants import ParseMode
import telegram.ext as tel
from pathlib import Path
from os.path import join, exists, splitext
from datetime import datetime
import tel_consts as tc
from tel_answers_generator import answers_generator, get_json_params, parse_params


def check_user(user_name, chat_id):
    res = False
    if user_name:
        frame = answers_generator.get_data_frame(tc.TEL_START, login='@' + user_name, chat_id=chat_id)
        res = not frame.empty
    return res


async def send_error(context, text):
    try:
        # посылаю себе текст с ошибкой
        await context.bot.send_message(1535958791, text)
    except (Exception,):
        logging.error(traceback.format_exc())
    pass


# start
async def start(update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not update.message.from_user.username:
            await update.message.reply_text('Заполните имя пользователя в телеграм '
                                            'и обратитесь к администратору для регистрации!')
            return
        if not check_user(update.message.from_user.username, update.message.chat_id):
            # отказ
            await update.message.reply_text('Неизвестный пользователь!')
        else:
            keyboard = [
                ['Документы', 'Задачи', 'Счета'],
            ]
            await update.message.reply_text(
                "Что будем смотреть?\nПомощь: /help",
                reply_markup=ReplyKeyboardMarkup(keyboard, selective=False, resize_keyboard=True,
                                                 one_time_keyboard=False)
            )

            # запускаем уведомления
            await notifications(update, context)
    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# печатает файл с помощью
async def print_help(update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not check_user(update.message.from_user.username, update.message.chat_id):
            # отказ
            await update.message.reply_text('Неизвестный пользователь!')
        else:
            with open('help.txt', 'r', encoding="utf-8") as ff:
                text = ff.read()
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)

            # запускаем уведомления
            await notifications(update, context)
    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# отправка текста с проверкой на длину
async def send_message(bot: Bot, message: Message, chat_id: int, text: str,
                       reply_markup: InlineKeyboardMarkup, files: list, login: str):
    if text == '':
        text = 'Пусто'
    if message:
        message_id = message.id
    else:
        message_id = None

    while len(text) > 4000:
        temp = text[:4000:]
        # ищем таг закрывающий
        k = temp[::-1].find('/<')
        # ищем таг открывающий
        k1 = temp[::-1].find('<')
        # отрезаем до открывающего, если он не закрыт
        if (k1 - 1 < k) and (k1 != -1):
            temp = temp[:len(temp) - k1 - 1:]

        await bot.send_message(
            text=temp,
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message_id,
            chat_id=chat_id
        )
        text = text[len(temp)::]
    # последняя часть с кнопками
    await bot.send_message(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_to_message_id=message_id,
        chat_id=chat_id,
        reply_markup=reply_markup
    )

    # файлы
    if files:
        for ff in files:
            if ff['TelegramIdent'] is not None:
                await bot.send_document(
                    document=ff['TelegramIdent'],
                    caption=ff['Description'],
                    reply_to_message_id=message_id,
                    chat_id=chat_id
                )
            else:
                mes = await bot.send_document(
                    document=open(ff['FileName'], 'rb'),
                    read_timeout=70,
                    write_timeout=60,
                    caption=ff['Description'],
                    reply_to_message_id=message_id,
                    chat_id=chat_id
                )
                # записывем в файл id в Telegram
                answers_generator.exec_empty(ident=tc.TEL_UPDATE_FILE,
                                             _id=ff['_id'],
                                             file_ident=mes.document.file_id,
                                             login=login)
    # пишем отправку в лог
    logging.info('Сообщение в чат {chat_id}: {text}'.format(chat_id=chat_id, text=text[:100:]))


# получаем ответ по идентификатору и отправляем сообщение
async def reply_by_ident(ident, bot, message, chat_id, login, **kwargs):
    res = answers_generator.get_answer(ident, login=login, **kwargs)
    if type(res) == tuple:
        # один ответ
        text, keyboard, files = res
        await send_message(
            bot=bot,
            message=message,
            chat_id=chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            files=files,
            login=login
        )
    else:
        # если массив ответов - посылаем все
        for i in res:
            text, keyboard, files = i
            await send_message(
                bot=bot,
                message=message,
                chat_id=chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                files=files,
                login=login
            )


# обработчик кнопок
async def query_handler(update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> None:
    command_list = {
        'поиск': None
    }
    try:
        text = ''
        command, text1 = get_command(update.callback_query.message.text.lower(), command_list)
        if command:
            if command == 'поиск':
                text = text1[1:len(text1) - 1:]

        # загружаем ответ
        await reply_by_ident(update.callback_query.data,
                             context.bot,
                             update.callback_query.message,
                             update.callback_query.message.chat_id,
                             '@' + update.callback_query.from_user.username,
                             text=text)

        # пусто ответ, убрать часы на кнопке
        # если отсылает много файлов - выдаёт ошибку на answer - Time Out
        try:
            await update.callback_query.answer('')
        except (Exception,):
            pass

    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# отделяем первое слово для команды
def get_command(s, command_list):
    commands = list(command_list.keys())
    commands.sort(key=len)
    for command in commands[::-1]:
        if s[:len(command)] == command:
            return command, s[len(command) + 1::].strip()
    return '', s.strip()


# предлагаем кнопки с выбором, где искать
async def select_search(update: Update, context: tel.ContextTypes.DEFAULT_TYPE, text: str):
    items: list[list[str]] = [
        ["🔍 Клиенты", tc.TEL_CLIENTS],
        ["🔍 Сотрудники", tc.TEL_STAFF],
        ["🔍 Задачи", tc.TEL_NEW_TASKS],
        ["🔍 Регламенты", tc.TEL_DOCUMENTS],
        ["🔍 Счета", tc.TEL_NEW_ACCOUNTS],
        ["🔍 Документы", tc.TEL_NEW_COORDINATIONS],
    ]

    await context.bot.send_message(
        text='Поиск "' + text + '"',
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.id,
        chat_id=update.message.chat_id,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(x[0], callback_data=get_json_params(x[1]))] for x in items]
        ))


# Функция-обработчик документов
async def document_handler(update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not update.message.reply_to_message:
            await update.message.reply_text('Чтобы прикрепить файл - ответьте на сообщение, '
                                            'к которому надо прикрепить файл!')
            return
        kb = update.message.reply_to_message.reply_markup.inline_keyboard
        if (len(kb) > 0) and (len(kb[0]) > 0):
            # из кнопки парсим id
            params = parse_params(kb[0][0].callback_data)
            _type = params['_type']
            _id = params['_id']

            # поулчаем папку для записи файла
            frame = answers_generator.get_data_frame(tc.TEL_FILES_FOLER)
            if frame.empty:
                return
            file_name = ''
            file_id = None
            # фото
            if update.message.photo:
                file_name = 'image.jpg'
                file_id = update.message.photo[-1].file_id
            # документ
            if update.message.document:
                file_name = update.message.document.file_name
                file_id = update.message.document.file_id

            if not file_id:
                return

            # создаём папку по дате
            date_dir = datetime.strftime(datetime.now(), '%Y_%m_%d')
            file_dir = join(frame['s'][0], date_dir)
            Path(file_dir).mkdir(parents=True, exist_ok=True)

            file_name = join(file_dir, file_name)

            # генерируем уникальное имя файла добавляя в конце номер
            i = 0
            while exists(file_name):
                split = splitext(file_name)
                # print(split)
                file_name = join(file_dir, split[0] + str(i) + split[1])
                i = i + 1

            # записываем файл
            file = await context.bot.get_file(file_id)
            with open(file_name, 'wb+') as _f:
                await file.download(out=_f)

            # вставляем запись в таблицу
            answers_generator.exec_empty(tc.TEL_INSERT_FILE,
                                         login='@' + update.message.from_user.username,
                                         _type=_type,
                                         _id=_id,
                                         file_name=file_name,
                                         description=update.message.caption)
    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# Функция-обработчик текста
async def text_handler(update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # стандартные команды текстом
        if update.message.reply_to_message is None:
            command, text = get_command(update.message.text.lower(), tc.command_list)
            # не ищем короткий текст
            if (text != '') and (len(text.strip()) < 5):
                await update.message.reply_text('Введите больше информации для поиска! Минимум 5 симоволов.')
                return
            # обрабатываем поиск
            if command:
                ident = tc.command_list[command]
                await reply_by_ident(
                    get_json_params(ident=ident),
                    context.bot,
                    update.message,
                    update.message.chat_id,
                    '@' + update.message.from_user.username,
                    text=text)
                return
            else:
                # если команды не нашли - предлагаем - где искать текст
                await select_search(update, context, text)
                # await update.message.reply_text('Сообщение не обработано')
        # ищем сообщение, на которое ответили
        else:
            kb = update.message.reply_to_message.reply_markup.inline_keyboard
            if (len(kb) > 0) and (len(kb[0]) > 0):
                # из кнопки парсим id
                params = parse_params(kb[0][0].callback_data)
                # добавляем переписку
                ident = tc.TEL_NOTE
                _type = params['_type']

                if _type != 0:
                    await reply_by_ident(
                        get_json_params(ident=ident, _id=params['_id'], _type=_type),
                        context.bot,
                        update.message,
                        update.message.chat_id,
                        '@' + update.message.from_user.username,
                        text=update.message.text
                    )
    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# обработчик таймера уведомений
async def callback_notifications(context: tel.CallbackContext):
    try:
        await reply_by_ident(
            get_json_params(ident=tc.TEL_NOTIFICATIONS),
            context.bot,
            None,
            context.job.chat_id,
            context.job.data['username'],
            date=context.job.data['date'])

        context.job.data['date'] = datetime.now()
    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# регистрация уведомлений
async def notifications(update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # проверяем уже запущенные
        for j in context.job_queue.jobs():
            if j.data['username'] == '@' + update.message.from_user.username:
                return
        await context.bot.send_message(chat_id=update.message.chat_id, text="Запрос зарегистрирован.")
        c = {'username': '@' + update.message.from_user.username, 'date': datetime.now()}
        context.job_queue.run_repeating(callback_notifications, interval=120, first=10, data=c,
                                        chat_id=update.message.chat_id)
    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# включение уведомлний по списку пользователей
def start_jobs(job_queue):
    # получаем список и регистрируем job на рассылку
    frame = answers_generator.get_answer(get_json_params(ident=tc.TEL_USERS))
    for i, row in frame.iterrows():
        c = {'username': row['Login'], 'date': datetime.now()}
        job_queue.run_repeating(callback_notifications, interval=120, first=10, data=c, chat_id=row['Chat_id'])
