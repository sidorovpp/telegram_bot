import tel_consts as tc
from generators.tel_custom_generator import CustomGenerator
from generators.tel_answers_generator import get_doc_with_notes, AnswersGenerator, get_json_params
from telegram import InlineKeyboardButton
import datetime


class ShowSheetsGenerator(CustomGenerator):
    def __init__(self, base_generator: AnswersGenerator):
        super().__init__(base_generator)
        self.base_generator.proc_list.update(
            {
                tc.TEL_SHOW_SHEETS: self.get_show_sheets,
                tc.TEL_SHOW_SHEET: self.get_show_sheet,
            })

    # вызов смотрового листа
    async def try_call_by_id(self, ident, **kwargs):
        if ident == tc.TEL_SHOW_SHEET_ID:
            # получаем клиента
            frame = await self.base_generator.get_frame(tc.TEL_GET_CLIENT_FROM_SHOW_SHEET, _id=kwargs['_id'])
            # пишем также в клиента и вызываем клиента
            return await self.base_generator.get_answer(
                ident=get_json_params(
                    ident=tc.TEL_NOTE,
                    _type=tc.TEL_CLIENT_ID,
                    _id=str(frame['client_id'][0]), ),
                login=kwargs['login'],
                text=kwargs['text']
            )
        else:
            return None

    # смотровые листы
    async def get_show_sheets(self, **kwargs):
        # получаем дату из параметров
        if 'custom' in kwargs:
            custom = kwargs['custom']
        else:
            custom = int(datetime.datetime.now().timestamp())

        # предыдущая дата
        before = datetime.datetime.fromtimestamp(custom) + datetime.timedelta(days=-1)
        before = int(before.timestamp())
        # следующая дата
        after = datetime.datetime.fromtimestamp(custom) + datetime.timedelta(days=1)
        after = int(after.timestamp())

        # получаем данные
        kwargs['ident'] = tc.TEL_SHOW_SHEETS
        # подсовываем отформатированную дату
        kwargs['date'] = datetime.date.fromtimestamp(custom).strftime('%Y%m%d')
        res = await self.base_generator.get_item_list(**kwargs)
        text, keyboard, files = res

        text = 'Дата: ' + datetime.date.fromtimestamp(custom).strftime('%d.%m.%Y') + '\r\n' + text

        # добавляем кнопки сдвига дат
        keyboard.append([
            InlineKeyboardButton('⬅️',
                                 callback_data=get_json_params(
                                     ident=tc.TEL_SHOW_SHEETS,
                                     custom=before
                                 )),
            InlineKeyboardButton('➡️',
                                 callback_data=get_json_params(
                                     ident=tc.TEL_SHOW_SHEETS,
                                     custom=after
                                 ))
        ])

        return text, keyboard, files

    # смотровой лист
    async def get_show_sheet(self, ident, **kwargs):
        frame = await self.base_generator.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            keyboard_items = \
                [
                    [
                        ["✉️ SMS", {"ident": tc.TEL_SEND_SMS, "_id": str(frame['_id'][0]),
                                    "_type": tc.TEL_SHOW_SHEET_ID}],
                        ["📩 Ввести код", {"ident": tc.TEL_CHECK_SMS, "_id": str(frame['_id'][0]),
                                          "_type": tc.TEL_SHOW_SHEET_ID}],
                        ["🚹 Клиент", {"ident": tc.TEL_CLIENT, "_id": str(frame['Client_id'][0])}],
                    ],
                    [
                        ["📝 Комментарий", {"ident": tc.TEL_NOTE, "_type": tc.TEL_SHOW_SHEET_ID,
                                           "_id": str(frame['_id'][0])}],
                        ["🏘️ Показы", {"ident": tc.TEL_SHOW_SHEETS}],
                    ]
                ]
            text = frame['Info'][0].format_map(tc.img_lib)
            text = get_doc_with_notes(text, frame)
            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []
