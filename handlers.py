import io
import json
import logging
import traceback
from telegram import Update, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
import telegram.ext as tel
from datetime import datetime, timedelta
import tel_consts as tc
from tel_answers_generator import answers_generator, get_json_params, parse_params
from tel_menu import get_main_menu, make_buttons_menu
from utils import create_shared_file, read_qr_code, send_error
from handlers_common import reply_by_ident


async def check_user(user_name, chat_id):
    res = False
    if user_name:
        frame = await answers_generator.get_data_frame(tc.TEL_START, login='@' + user_name, chat_id=chat_id)
        res = not frame.empty
    return res


# start
async def start(update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.message.chat.type == 'group' or update.message.chat.type == 'supergroup':
            return

        if not update.message.from_user.username:
            await update.message.reply_text('Заполните имя пользователя в телеграм '
                                            'и обратитесь к администратору для регистрации!')
            return
        if not await check_user(update.message.from_user.username, update.message.chat_id):
            # отказ
            await update.message.reply_text('Неизвестный пользователь!')
        else:
            keyboard = make_buttons_menu(get_main_menu(tc.TEL_MAIN_MENU))
            await update.message.reply_text(
                "Что будем смотреть?\nПомощь: /help",
                reply_markup=ReplyKeyboardMarkup(keyboard, selective=False, resize_keyboard=True,
                                                 one_time_keyboard=False)
            )

            # запускаем уведомления
            # await notifications(update, context)
    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# печатает файл с помощью
async def print_help(update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.message.chat.type == 'group' or update.message.chat.type == 'supergroup':
            return

        if not await check_user(update.message.from_user.username, update.message.chat_id):
            # отказ
            await update.message.reply_text('Неизвестный пользователь!')
        else:
            with open('help.txt', 'r', encoding="utf-8") as ff:
                text = ff.read()
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)

            # запускаем уведомления
            # await notifications(update, context)
    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# подменяем клавиатуру по меню
async def replace_keyboard(menu: int, item: int, _id: int, message: Message):
    keyboard_items = answers_generator.menu.get_keyboard_items(menu, item, _id)
    keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                for x in keyboard_items]
    await message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))


# обработчик кнопок
async def query_handler(update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> None:
    command_list = {
        'поиск': None
    }
    try:

        if update.callback_query.message.chat.type == 'group' or \
                update.callback_query.message.chat.type == 'supergroup':
            return

        text = ''
        command, text1 = get_command(update.callback_query.message.text.lower(), command_list)
        if command:
            if command == 'поиск':
                text = text1[1:len(text1) - 1:]

        # проверяем меню
        params = json.loads(update.callback_query.data)
        if params['ident'] == tc.TEL_MENU:
            await replace_keyboard(menu=params['_type'],
                                   item=params['ext'],
                                   _id=params['_id'],
                                   message=update.callback_query.message)
            return

        if not update.callback_query.from_user.username:
            await update.callback_query.answer('Неизвестный пользователь')
            return

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
        ["🔍 Контрагенты", tc.TEL_CONTR_CLIENTS],
        ["🔍 Задачи", tc.TEL_NEW_TASKS],
        ["🔍 Регламенты", tc.TEL_DOCUMENTS],
        ["🔍 Счета", tc.TEL_NEW_ACCOUNTS],
        ["🔍 Документы", tc.TEL_NEW_COORDINATIONS],
        ["🔍 Заявки", tc.TEL_PETITIONS],
        ["🔍 Показы", tc.TEL_SHOW_SHEETS],
        ["🔍 Спецификация", tc.TEL_SPECIFICATION],
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
        if update.message.chat.type == 'group' or update.message.chat.type == 'supergroup':
            return

        if not update.message.reply_to_message:
            # пробуем считать QR
            check = False

            if update.message.photo:
                file_name = 'image.png'
                file_id = update.message.photo[-1].file_id

                # записываем файл
                file = await context.bot.get_file(file_id)
                await file.download_to_drive(file_name)
                # читаем код
                value = read_qr_code(file_name)
                if value:
                    check = True
                    value = value.decode("utf-8")
                    await update.message.reply_text(value)
                    await reply_by_ident(get_json_params(tc.TEL_SPECIFICATION),
                                         context.bot,
                                         update.message,
                                         update.message.chat_id,
                                         '@' + update.message.from_user.username,
                                         text=value)

            # не обработано
            if not check:
                await update.message.reply_text('Чтобы прикрепить файл - ответьте на сообщение, '
                                                'к которому надо прикрепить файл!')
            return

        # отвечаем на сообщение - добавляем в файлы
        kb = update.message.reply_to_message.reply_markup.inline_keyboard
        if (len(kb) > 0) and (len(kb[0]) > 0):
            # из кнопки парсим id
            params = parse_params(kb[0][0].callback_data)
            _type = params['_type']
            _id = params['_id']

            # получаем папку для записи файла
            frame = await answers_generator.get_data_frame(tc.TEL_FILES_FOLDER)
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

            # не использую os.join и прочее - чтобы собрать строку под windows в Linux
            # строка нужна в формате Windows для сохранения в базе
            # создаём папку по дате
            date_dir = datetime.strftime(datetime.now(), '%Y_%m_%d')
            file_dir = frame['s'][0] + '\\' + date_dir
            # записываем файл
            file = await context.bot.get_file(file_id)
            f = io.BytesIO()
            await file.download_to_memory(f)
            f.seek(0)
            file_name = create_shared_file(file_dir, file_name, f)
            file_name = file_dir + '\\' + file_name

            # вставляем запись в таблицу
            await answers_generator.exec_empty(tc.TEL_INSERT_FILE,
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
        # если группа
        if update.message.chat.type == 'group' or update.message.chat.type == 'supergroup':
            if update.message.text.lower() == 'chat_id':
                # записываем id чата в таблицу
                await answers_generator.exec_empty(
                    tc.TEL_SAVE_CHAT,
                    chat_id=update.message.chat.id,
                    description=update.message.chat.title)
            return

        if update.message is None:
            return
        if update.message.reply_to_message is None:
            # сначала смотрим меню
            menu = get_main_menu(update.message.text)
            if menu:
                keyboard = make_buttons_menu(menu)
                await update.message.reply_text(
                    "Выберите кнопку",
                    reply_markup=ReplyKeyboardMarkup(keyboard, selective=False, resize_keyboard=True,
                                                     one_time_keyboard=False)
                )
                return

            # если не меню - смотрим команды
            # command_list -стандартные команды текстом
            command, text = get_command(update.message.text.lower(), tc.command_list)
            # не ищем короткий текст
            if (text != '') and (len(text.strip()) < 5):
                await update.message.reply_text('Введите больше информации для поиска! Минимум 5 символов.')
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
            sended = False
            if update.message.reply_to_message.reply_markup:
                kb = update.message.reply_to_message.reply_markup.inline_keyboard
                if (len(kb) > 0) and (len(kb[0]) > 0):
                    # из кнопки парсим id
                    params = parse_params(kb[0][0].callback_data)
                    # добавляем переписку
                    ident = tc.TEL_NOTE
                    _type = params['_type']

                    sended = True
                    if _type != 0:
                        await reply_by_ident(
                            get_json_params(ident=ident, _id=params['_id'], _type=_type),
                            context.bot,
                            update.message,
                            update.message.chat_id,
                            '@' + update.message.from_user.username,
                            text=update.message.text
                        )
            if not sended:
                await context.bot.send_message(update.message.chat_id, 'Для добавления переписки отвечать надо на '
                                                                       'сообщение, под которым расположены кнопки.')
    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# обработчик таймера уведомлений
async def callback_notifications(context: tel.CallbackContext):
    try:
        frame = await answers_generator.get_answer(get_json_params(ident=tc.TEL_USERS))
        for i, row in frame.iterrows():
            user = row['Login']
            chat_id = row['Chat_id']
            await reply_by_ident(
                get_json_params(ident=tc.TEL_NOTIFICATIONS),
                context.bot,
                None,
                chat_id,
                login=user,
                date=datetime.now() - timedelta(minutes=2))

    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, 'Пользователь: ' + context.job.data['username'])
        await send_error(context, traceback.format_exc())


# отправка сообщений
async def send_messages(context: tel.CallbackContext):
    try:
        frame = await answers_generator.get_frame(tc.TEL_GET_MESSAGES)
        for i, row in frame.iterrows():
            try:
                s = row['message'].format_map(tc.img_lib)
                await context.bot.send_message(row['chat_id'], s, parse_mode=ParseMode.HTML)
            except (Exception,):
                await send_error(context, traceback.format_exc())
            await answers_generator.exec_empty(tc.TEL_SET_MESSAGE_SENT, id=row['id'])
    except (Exception,):
        logging.error(traceback.format_exc())
        await send_error(context, traceback.format_exc())


# включение уведомлений по списку пользователей
def start_jobs(job_queue):
    # получаем список и регистрируем job на рассылку
    job_queue.run_repeating(callback_notifications, interval=120, first=10, data={})

    job_queue.run_repeating(send_messages, interval=60, first=10, data={})
