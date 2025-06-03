import tel_consts as tc
from generators.tel_custom_generator import CustomGenerator
from generators.tel_answers_generator import replace_params, get_doc_with_notes, AnswersGenerator, get_json_params
from telegram import InlineKeyboardButton
import requests
import json


class ClientsGenerator(CustomGenerator):
    def __init__(self, base_generator: AnswersGenerator):
        super().__init__(base_generator)
        self.base_generator.proc_list.update(
            {tc.TEL_CLIENT: self.get_client,
             tc.TEL_CONTR_CLIENT: self.get_contr_client,
             tc.TEL_CLIENT_SCORING: self.get_client_scoring,
             # tc.TEL_INN_REQUEST: self.get_inn_request,
             })

    # вызов клиента
    async def try_call_by_id(self, ident, **kwargs):
        if ident == tc.TEL_CLIENT_ID:
            return await self.get_client(tc.TEL_CLIENT, _id=kwargs['_id'], login=kwargs['login'])
        else:
            return None

    # клиент
    async def get_client(self, ident, **kwargs):
        keyboard_items = \
            [
                [
                    ["📝 Комментарий", {"ident": tc.TEL_NOTE, "_type": tc.TEL_CLIENT_ID,
                                       "_id": kwargs["_id"]}],
                    ["📁 Файлы", {"ident": tc.TEL_FILES, "_id": kwargs["_id"],
                                 "_type": tc.TEL_CLIENT_ID}],
                ]
            ]
        frame = await self.base_generator.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0]
            text = get_doc_with_notes(text, frame)
            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    # контрагент
    async def get_contr_client(self, ident, **kwargs):
        keyboard_items = \
            [
                [

                    ["🕵️ Скоринг", {"ident": tc.TEL_CLIENT_SCORING, "_id": kwargs["_id"]}],
                    ["📜 ИНН", {"ident": tc.TEL_INN, "_id": kwargs["_id"]}],
                ],
                # [
                #     ["🔍 Запросить ИНН в налоговой", {"ident": tc.TEL_INN_REQUEST, "_id": kwargs["_id"]}],
                # ]
            ]
        frame = await self.base_generator.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0]
            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    async def get_client_scoring(self, ident, **kwargs):
        headers = {'Authorization': 'Bearer ' + tc.TEL_SCORING_TOKEN, 'Content-Type': 'application/json'}
        res = requests.post(tc.TEL_SCORING_URL, data=json.dumps({'id': kwargs['_id']}), headers=headers)
        res = res.json()
        if res['result'] != '':
            return res['result'], [], []
        else:
            frame = await self.base_generator.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
            text = frame['Info'][0].format_map(tc.img_lib)
            return text, [], []

    # запрашиваем ИНН на сайте налоговой по параметрам клиента
    # async def get_inn_request(self, ident, **kwargs):
    #     frame = await self.get_data_frame(tc.TEL_CLIENT_DATA, _id=kwargs['_id'])
    #     inn = await get_inn(frame)
    #     return inn, [], []
