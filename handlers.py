import io
import json
import logging
import traceback
from telegram import Update, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest
import telegram.ext as tel
from datetime import datetime
import tel_consts as tc
from tel_answers_generator import answers_generator, get_json_params, parse_params
from tel_menu import get_main_menu, make_buttons_menu
from utils import get_shared_file, create_shared_file, read_qr_code

THEME, TEXT, URGENCY, RECEIVER_TEXT, RECEIVER, WORKGROUP_TEXT, WORKGROUP = range(10000, 10007)


# класс для обработки добавления новой задачи
class TaskHandler:
    def __init__(self):
        self.user_data = {}
        self.urgency_items = \
            [
                [["Срочно", 6]],
                [["Очень важно", 1]],
                [["Важно", 2]],
                [["Нормально", 3]],
                [["Не важно", 4]],
            ]

        self.conv_handler = tel.ConversationHandler(
            entry_points=[tel.MessageHandler(tel.filters.Regex("(?i)^Новая задача$"), self.new_task)],
            allow_reentry=True,
            states={
                THEME: [tel.MessageHandler(tel.filters.TEXT, self.task_theme)],
                TEXT: [tel.MessageHandler(tel.filters.TEXT, self.task_text)],
                URGENCY: [tel.CallbackQueryHandler(self.task_urgency)],
                RECEIVER_TEXT: [tel.MessageHandler(tel.filters.TEXT, self.task_receiver_text)],
                RECEIVER: [tel.CallbackQueryHandler(self.task_receiver)],
                WORKGROUP_TEXT: [tel.MessageHandler(tel.filters.TEXT, self.task_work_group_text)],
                WORKGROUP: [tel.CallbackQueryHandler(self.task_work_group)]
            },

            fallbacks=[tel.MessageHandler(tel.filters.Regex("(?i)^Отмена$"), self.task_cancel)]
        )

    # отмена
    async def task_cancel(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            self.user_data[update.message.from_user.username] = []
            await update.message.reply_text('Создание задачи отменено')
            return tel.ConversationHandler.END
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # старт
    async def new_task(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            self.user_data[update.message.from_user.username] = {}
            await update.message.reply_text('Тема задачи:')
            return THEME
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # тема
    async def task_theme(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            self.user_data[update.message.from_user.username]['theme'] = update.message.text
            await update.message.reply_text('Текст задачи:')
            return TEXT
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # текст
    async def task_text(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            self.user_data[update.message.from_user.username]['task'] = update.message.text
            keyboard = [[InlineKeyboardButton(y[0], callback_data=y[1]) for y in x]
                        for x in self.urgency_items]
            await update.message.reply_text('Важность задачи:', reply_markup=InlineKeyboardMarkup(keyboard))
            return URGENCY
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # важность
    async def task_urgency(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            self.user_data[update.callback_query.from_user.username]['urgency'] = update.callback_query.data
            await update.callback_query.message.reply_text('Получатель (часть ФИО для поиска):')
            await update.callback_query.answer('')
            return RECEIVER_TEXT
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # получатель текст
    async def task_receiver_text(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            self.user_data[update.message.from_user.username]['receiver_text'] = update.message.text
            frame = answers_generator.get_frame(tc.TEL_FIND_STAFF, text=update.message.text)
            if len(frame) == 0:
                await update.message.reply_text('Получатель не найден!')
                return RECEIVER_TEXT
            items = []
            for index, row in frame.iterrows():
                items.append([[row['FIO'], row['id']]])
            keyboard = [[InlineKeyboardButton(y[0], callback_data=y[1]) for y in x]
                        for x in items]
            await update.message.reply_text('Выберите получателя:', reply_markup=InlineKeyboardMarkup(keyboard))
            return RECEIVER
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # получатель
    async def task_receiver(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            user = update.callback_query.from_user.username
            self.user_data[user]['receiver'] = update.callback_query.data
            await update.callback_query.message.reply_text('Рабочая группа (часть названия для поиска):')
            await update.callback_query.answer('')
            return WORKGROUP_TEXT
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # рабочая группа текст
    async def task_work_group_text(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            self.user_data[update.message.from_user.username]['work_group_text'] = update.message.text
            frame = answers_generator.get_frame(tc.TEL_FIND_WORK_GROUP, text=update.message.text)
            if len(frame) == 0:
                await update.message.reply_text('Рабочая группа не найдена!')
                return RECEIVER_TEXT
            items = []
            for index, row in frame.iterrows():
                items.append([[row['Name'], row['id']]])
            keyboard = [[InlineKeyboardButton(y[0], callback_data=y[1]) for y in x]
                        for x in items]
            await update.message.reply_text('Выберите рабочую группу:', reply_markup=InlineKeyboardMarkup(keyboard))
            return WORKGROUP
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # рабочая группа
    async def task_work_group(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            user = update.callback_query.from_user.username
            self.user_data[user]['work_group'] = update.callback_query.data
            frame = answers_generator.get_frame(tc.TEL_ADD_TASK,
                                                login='@' + user,
                                                theme=self.user_data[user]['theme'],
                                                task=self.user_data[user]['task'],
                                                urgency=self.user_data[user]['urgency'],
                                                receiver=self.user_data[user]['receiver'],
                                                work_group=self.user_data[user]['work_group']
                                                )
            items = [[["📓 Посмотреть", get_json_params(
                ident=tc.TEL_TASK,
                _id=int(frame['task_id'].values[0]))]]]
            keyboard = [[InlineKeyboardButton(y[0], callback_data=y[1]) for y in x]
                        for x in items]
            await update.callback_query.message.reply_text('Готово!', reply_markup=InlineKeyboardMarkup(keyboard))
            await update.callback_query.answer('')
            return tel.ConversationHandler.END
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END


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
            keyboard = make_buttons_menu(get_main_menu('Главное меню'))
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

        # пытаюсь отправить как HTML, в случае ощшибки - кидаю как обычный текст
        try:
            await bot.send_message(
                text=temp,
                parse_mode=ParseMode.HTML,
                reply_to_message_id=message_id,
                chat_id=chat_id
            )
        except BadRequest:
            await bot.send_message(
                text=temp,
                parse_mode=None,
                reply_to_message_id=message_id,
                chat_id=chat_id
            )

        text = text[len(temp)::]
    # последняя часть с кнопками

    # пытаюсь отправить как HTML, в случае ощшибки - кидаю как обычный текст
    try:
        await bot.send_message(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message_id,
            chat_id=chat_id,
            reply_markup=reply_markup
        )
    except BadRequest:
        await bot.send_message(
            text=temp,
            parse_mode=None,
            reply_to_message_id=message_id,
            chat_id=chat_id
        )

    # файлы
    if files:
        for ff in files:
            sended = False
            if ff['TelegramIdent'] is not None:
                try:
                    await bot.send_document(
                        document=ff['TelegramIdent'],
                        caption=ff['Description'],
                        reply_to_message_id=message_id,
                        chat_id=chat_id
                    )
                    sended = True
                except (Exception,):
                    sended = False
            if not sended:
                f = get_shared_file(ff['FileName'])
                if f:
                    f.seek(0)
                    mes = await bot.send_document(
                        document=f,
                        read_timeout=70,
                        write_timeout=60,
                        caption=ff['Description'],
                        reply_to_message_id=message_id,
                        chat_id=chat_id
                    )
                    f.close()
                    # записывем в файл id в Telegram
                    answers_generator.exec_empty(ident=tc.TEL_UPDATE_FILE,
                                                 _id=ff['_id'],
                                                 file_ident=mes.document.file_id,
                                                 login=login)
    # пишем отправку в лог
    logging.info('Сообщение в чат {chat_id}: {text}'.format(chat_id=chat_id, text=text[:100:]))


# подменяем клавиатуру по меню
async def replace_keyboard(menu: int, item: int, _id: int, message: Message):
    keyboard_items = answers_generator.menu.get_keyboard_items(menu, item, _id)
    keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                for x in keyboard_items]
    await message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))


# получаем ответ по идентификатору и отправляем сообщение
async def reply_by_ident(ident, bot, message, chat_id, login, **kwargs):
    res = answers_generator.get_answer(ident, login=login, **kwargs)
    if res is None:
        return
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

        # проверяем меню
        params = json.loads(update.callback_query.data)
        if params['ident'] == tc.TEL_MENU:
            await replace_keyboard(menu=params['_type'],
                                   item=params['ext'],
                                   _id=params['_id'],
                                   message=update.callback_query.message)
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
        ["🔍 Задачи", tc.TEL_NEW_TASKS],
        ["🔍 Регламенты", tc.TEL_DOCUMENTS],
        ["🔍 Счета", tc.TEL_NEW_ACCOUNTS],
        ["🔍 Документы", tc.TEL_NEW_COORDINATIONS],
        ["🔍 Заявки", tc.TEL_PETITIONS],
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

            # поулчаем папку для записи файла
            frame = answers_generator.get_data_frame(tc.TEL_FILES_FOLDER)
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
            create_shared_file(file_dir, file_name, f)
            file_name = file_dir + '\\' + file_name

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
        # c = {'username': row['Login'], 'date': datetime.now() + timedelta(days=-1)}
        c = {'username': row['Login'], 'date': datetime.now()}
        job_queue.run_repeating(callback_notifications, interval=120, first=10, data=c, chat_id=row['Chat_id'])
