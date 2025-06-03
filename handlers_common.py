from generators.tel_answers_generator import answers_generator
from utils import get_shared_file
from telegram import InlineKeyboardMarkup, Message, Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest
import logging
import tel_consts as tc


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

        # пытаюсь отправить как HTML, в случае ошибки - кидаю как обычный текст
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

    # пытаюсь отправить как HTML, в случае ошибки - кидаю как обычный текст
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
            text=text,
            parse_mode=None,
            reply_to_message_id=message_id,
            chat_id=chat_id,
            reply_markup=reply_markup
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
                    # записываем в файл id в Telegram
                    await answers_generator.exec_empty(ident=tc.TEL_UPDATE_FILE,
                                                       _id=ff['_id'],
                                                       file_ident=mes.document.file_id,
                                                       login=login)
    # пишем отправку в лог
    logging.info('Сообщение в чат {chat_id}: {text}'.format(chat_id=chat_id, text=text[:100:]))


# получаем ответ по идентификатору и отправляем сообщение
async def reply_by_ident(ident, bot, message, chat_id, login, **kwargs):
    res = await answers_generator.get_answer(ident, login=login, **kwargs)
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
