from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
import telegram.ext as tel
import logging
import traceback
from utils import send_sms_to_service, send_error
import json
from generators.tel_answers_generator import answers_generator, get_json_params
import tel_consts as tc
from handlers_common import reply_by_ident
from inn import validate, only_digits

THEME, TEXT, URGENCY, RECEIVER_TEXT, RECEIVER, WORKGROUP_TEXT, WORKGROUP = range(10000, 10007)
CODE_TEXT = 11000
SEND_ANSWER = 12000
SEND_INN = 13000


# класс для обработки ответа в переписку
class NoteHandler:
    def __init__(self):
        self.user_data = {}

        self.conv_handler = tel.ConversationHandler(
            entry_points=[tel.CallbackQueryHandler(self.get_answer, pattern=r'{"ident": "note".*')],
            allow_reentry=True,
            states={
                SEND_ANSWER: [tel.MessageHandler(tel.filters.TEXT, self.send_answer)],
            },

            fallbacks=[tel.MessageHandler(tel.filters.Regex("(?i)^Отмена$"), self.note_cancel)]
        )

    # отмена
    async def note_cancel(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            self.user_data[update.message.from_user.username] = []
            await update.message.reply_text('Запись комментария отменена')
            return tel.ConversationHandler.END
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # старт
    async def get_answer(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            user = update.callback_query.from_user.username
            params = json.loads(update.callback_query.data)
            self.user_data[user] = {}
            self.user_data[user]['_id'] = params['_id']
            self.user_data[user]['_type'] = params['_type']
            await update.callback_query.message.reply_text('Напишите комментарий (для отмены - напишите Отмена):')
            await update.callback_query.answer('')
            return SEND_ANSWER
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    async def send_answer(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            if update.message.text.lower() == tc.TEL_CANCEL:
                return await self.note_cancel(update, context)
            user = update.message.from_user.username
            ident = tc.TEL_NOTE
            _type = self.user_data[user]['_type']
            _id = self.user_data[user]['_id']

            if _type != 0:
                await reply_by_ident(
                    get_json_params(ident=ident, _id=_id, _type=_type),
                    context.bot,
                    update.message,
                    update.message.chat_id,
                    '@' + update.message.from_user.username,
                    text=update.message.text
                )
            return tel.ConversationHandler.END
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END


# класс для добавления ИНН
class INNHandler:
    def __init__(self):
        self.user_data = {}

        self.conv_handler = tel.ConversationHandler(
            entry_points=[tel.CallbackQueryHandler(self.get_inn, pattern=r'{"ident": "inn".*')],
            allow_reentry=True,
            states={
                SEND_INN: [tel.MessageHandler(tel.filters.TEXT, self.send_inn)],
            },

            fallbacks=[tel.MessageHandler(tel.filters.Regex("(?i)^Отмена$"), self.note_cancel)]
        )

    # отмена
    async def note_cancel(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            self.user_data[update.message.from_user.username] = []
            await update.message.reply_text('Запись инн отменена')
            return tel.ConversationHandler.END
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # старт
    async def get_inn(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            user = update.callback_query.from_user.username
            params = json.loads(update.callback_query.data)
            self.user_data[user] = {}
            self.user_data[user]['_id'] = params['_id']
            await update.callback_query.message.reply_text('Напишите ИНН контрагента (для отмены - напишите Отмена):')
            await update.callback_query.answer('')
            return SEND_INN
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    async def send_inn(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            if update.message.text.lower() == tc.TEL_CANCEL:
                return await self.note_cancel(update, context)
            user = update.message.from_user.username
            _id = self.user_data[user]['_id']
            inn = update.message.text.lower().strip()
            inn = only_digits(inn)
            if not validate(inn):
                await update.message.reply_text('Введите корректный ИНН')
                return SEND_INN

            await answers_generator.exec_empty(tc.TEL_CONTR_INN, _id=_id, inn=inn)
            await update.message.reply_text('ИНН сохранён')
            await reply_by_ident(get_json_params(ident=tc.TEL_CONTR_CLIENT, _id=_id),
                                 context.bot,
                                 update.message,
                                 update.message.chat_id,
                                 '@' + update.message.from_user.username)

            return tel.ConversationHandler.END
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END


# класс для обработки СМС
class SMSHandler:
    def __init__(self):
        self.user_data = {}

        self.conv_handler = tel.ConversationHandler(
            entry_points=[tel.CallbackQueryHandler(self.get_code, pattern=r'{"ident": "sms.*')],
            allow_reentry=True,
            states={
                CODE_TEXT: [tel.MessageHandler(tel.filters.TEXT, self.send_code)],
            },

            fallbacks=[tel.MessageHandler(tel.filters.Regex("(?i)^Отмена$"), self.sms_cancel)]
        )

    # отмена
    async def sms_cancel(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            self.user_data[update.message.from_user.username] = []
            await update.message.reply_text('Запись кода СМС отменена')
            return tel.ConversationHandler.END
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # старт
    async def get_code(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            user = update.callback_query.from_user.username
            params = json.loads(update.callback_query.data)
            self.user_data[user] = {}
            _id = params['_id']
            if params['ident'] == tc.TEL_SEND_SMS:
                refresh = 1
            else:
                refresh = 0
            frame = await answers_generator.get_frame(tc.TEL_GET_SHOW_SHEET_CODE, _id=_id, refresh=refresh)
            phone = frame['Phone'].values[0]
            code = frame['Code'].values[0]
            self.user_data[user]['code'] = code
            self.user_data[user]['id'] = _id
            if params['ident'] == tc.TEL_SEND_SMS:
                text = 'После показа Вам помещения сообщите код менеджеру: ' + code
                # отправляем SMS
                await send_sms_to_service(text, phone, 'telegram_show_sheet')
                # пишем в лог
                await answers_generator.exec_empty(tc.TEL_INSERT_SMS_LOG,
                                                   login='@' + user,
                                                   phone=phone,
                                                   text=text)
            await update.callback_query.message.reply_text('Введите код, полученный от клиента:')
            await update.callback_query.answer('')
            return CODE_TEXT
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    async def send_code(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            if update.message.text.lower() == tc.TEL_CANCEL:
                return await self.sms_cancel(update, context)
            code = update.message.text
            user = update.message.from_user.username
            if code.strip() == self.user_data[user]['code']:
                await update.message.reply_text('✅ Код подтверждён!')
                _id = self.user_data[user]['id']
                frame = await answers_generator.get_frame(tc.TEL_CONFIRM_SHEET_CODE, _id=_id)
                # отправляем SMS
                message_text = tc.show_sheet_sms.format(staff_id=frame['Staff_id'].values[0],
                                                        show_sheet_id=_id)
                phone = frame['DigitalNumber'].values[0]
                await send_sms_to_service(message_text, phone, 'telegram_show_sheet')

            else:
                await update.message.reply_text('❌ Введён неправильный код!')
            return tel.ConversationHandler.END
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END


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
        if update.message.chat.type == 'group' or update.message.chat.type == 'supergroup':
            return tel.ConversationHandler.END
        try:
            self.user_data[update.message.from_user.username] = {}
            await update.message.reply_text('Тема задачи \n(для отмены напишите "Отмена"):')
            return THEME
        except (Exception,):
            logging.error(traceback.format_exc())
            await send_error(context, traceback.format_exc())
            return tel.ConversationHandler.END

    # тема
    async def task_theme(self, update: Update, context: tel.ContextTypes.DEFAULT_TYPE) -> int:
        try:
            if update.message.text.lower() == tc.TEL_CANCEL:
                return await self.task_cancel(update, context)
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
            if update.message.text.lower() == tc.TEL_CANCEL:
                return await self.task_cancel(update, context)
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
            frame = await answers_generator.get_frame(tc.TEL_FIND_STAFF, text=update.message.text)
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
            frame = await answers_generator.get_frame(tc.TEL_FIND_WORK_GROUP, text=update.message.text)
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
            frame = await answers_generator.get_frame(tc.TEL_ADD_TASK,
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
