import tel_consts as tc
from generators.tel_custom_generator import CustomGenerator
from generators.tel_answers_generator import replace_params, get_doc_with_notes, AnswersGenerator, get_json_params
from telegram import InlineKeyboardButton


class AccountsGenerator(CustomGenerator):
    def __init__(self, base_generator: AnswersGenerator):
        super().__init__(base_generator)
        self.base_generator.proc_list.update(
            {tc.TEL_ACCOUNT: self.get_account,
             tc.TEL_AGREE_ACCOUNT: self.get_agree_account,
             tc.TEL_DISAGREE_ACCOUNT: self.get_agree_account,
             tc.TEL_IGNORE_ACCOUNT: self.get_agree_account, })

    # вызов счёта
    async def try_call_by_id(self, ident, **kwargs):
        if ident == tc.TEL_ACCOUNT_ID:
            return await self.get_account(tc.TEL_ACCOUNT, _id=kwargs['_id'], login=kwargs['login'])
        else:
            return None

    # визируем счёт
    async def get_agree_account(self, ident, **kwargs):
        # помечаем прочитанной
        await self.base_generator.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Счета"
        return await self.base_generator.get_item_list(tc.TEL_NEW_ACCOUNTS, login=kwargs['login'])

    # информация по счёту
    async def get_account(self, ident, **kwargs):
        # загружаем меню
        index = await self.base_generator.add_menu(
            ident, tc.TEL_ACCOUNT_ID,
            [{"name": "🖋 Визы",
              "_json": '{{"ident": "{ident}", "_id": {_id}, "_type": {_type}}}'.format(
                  ident=tc.TEL_VISA,
                  _id=kwargs["_id"],
                  _type=tc.TEL_ACCOUNT_ID)}],
            **kwargs)

        # клавиатура
        keyboard_items = \
            [
                [
                    ["✅ За", {"ident": tc.TEL_AGREE_ACCOUNT,
                              "_id": kwargs["_id"],
                              "_type": tc.TEL_ACCOUNT_ID}],
                    ["❌ Против", {"ident": tc.TEL_DISAGREE_ACCOUNT,
                                  "_id": kwargs["_id"],
                                  "_type": tc.TEL_ACCOUNT_ID}],
                    ["⬆ На усмотрение", {"ident": tc.TEL_IGNORE_ACCOUNT,
                                         "_id": kwargs["_id"],
                                         "_type": tc.TEL_ACCOUNT_ID}],
                ],
                [
                    ["📁 Файлы", {"ident": tc.TEL_FILES, "_id": kwargs["_id"], "_type": tc.TEL_ACCOUNT_ID}],
                    ["🖋 Визы", {"ident": tc.TEL_VISA, "_id": kwargs["_id"], "_type": tc.TEL_ACCOUNT_ID}],
                    ["Кто смотрел 👀", {"ident": tc.TEL_READED,
                                       "_id": kwargs["_id"],
                                       "_type": tc.TEL_ACCOUNT_ID}],
                ],
                [
                    ["💸 Счета", {"ident": tc.TEL_NEW_ACCOUNTS}],
                    ["🖋 Виза/подпись", {"ident": tc.TEL_MENU, "_id": kwargs["_id"], "_type": index, "ext": -1}],
                ]
            ]

        frame = await self.base_generator.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = replace_params(frame['Info'][0], tc.img_lib)
            text = get_doc_with_notes(text, frame)

            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []
