import tel_consts as tc
from generators.tel_custom_generator import CustomGenerator
from generators.tel_answers_generator import replace_params, get_doc_with_notes, AnswersGenerator, get_json_params
from telegram import InlineKeyboardButton


class PetitionsGenerator(CustomGenerator):
    def __init__(self, base_generator: AnswersGenerator):
        super().__init__(base_generator)
        self.base_generator.proc_list.update(
            {tc.TEL_PETITION: self.get_petition,
             tc.TEL_PETITIONS_DSRIM: self.get_petitions_dsrim,
             tc.TEL_PETITIONS_BACK: self.get_petitions_back,
             tc.TEL_PETITIONS_DISAGREE: self.get_petitions_disagree,
             tc.TEL_PETITIONS_MY: self.get_petitions_my,
             tc.TEL_PETITIONS_DIR: self.get_petitions_dir, })

    # вызов заявки
    async def try_call_by_id(self, ident, **kwargs):
        if ident == tc.TEL_PETITION_ID:
            return await self.get_petition(tc.TEL_PETITION, _id=kwargs['_id'], login=kwargs['login'])
        else:
            return None

    # заявка
    async def get_petition(self, ident, **kwargs):
        # загружаем меню
        index = await self.base_generator.add_menu(ident, tc.TEL_PETITION_ID,
                                    [{"name": "🖋📃 Визы",
                                      "_json": '{{"ident": "{ident}", "_id": {_id}, "_type": {_type}}}'.format(
                                          ident=tc.TEL_VISA,
                                          _id=kwargs["_id"],
                                          _type=tc.TEL_PETITION_ID)}],
                                    **kwargs)
        keyboard_items = \
            [
                [
                    ["🖋📃 Визы", {"ident": tc.TEL_VISA, "_id": kwargs["_id"],
                                 "_type": tc.TEL_PETITION_ID}],
                    ["🖋 Виза/подпись", {"ident": tc.TEL_MENU, "_id": kwargs["_id"], "_type": index, "ext": -1}],
                    ["📁 Файлы", {"ident": tc.TEL_FILES, "_id": kwargs["_id"],
                                 "_type": tc.TEL_PETITION_ID}],
                ],
                [

                    ["🗓 График", {"ident": tc.TEL_PETITION_GRAPH, "_id": kwargs["_id"]}],
                    ["🚹 Клиенты", {"ident": tc.TEL_PETITION_CLIENTS, "_id": kwargs["_id"]}],
                    ["📝 Заявки", {"ident": tc.TEL_PETITIONS}],
                ]

            ]

        frame = await self.base_generator.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0].format_map(tc.img_lib)
            text = get_doc_with_notes(text, frame)
            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    async def get_petitions_dsrim(self, **kwargs):
        kwargs['ident'] = tc.TEL_PETITIONS
        kwargs['mode'] = 1
        return await self.base_generator.get_item_list(**kwargs)

    async def get_petitions_back(self, **kwargs):
        kwargs['ident'] = tc.TEL_PETITIONS
        kwargs['mode'] = 2
        return await self.base_generator.get_item_list(**kwargs)

    async def get_petitions_disagree(self, **kwargs):
        kwargs['ident'] = tc.TEL_PETITIONS
        kwargs['mode'] = 3
        return await self.base_generator.get_item_list(**kwargs)

    async def get_petitions_my(self, **kwargs):
        kwargs['ident'] = tc.TEL_PETITIONS
        kwargs['mode'] = 4
        return await self.base_generator.get_item_list(**kwargs)

    async def get_petitions_dir(self, **kwargs):
        kwargs['ident'] = tc.TEL_PETITIONS
        kwargs['mode'] = 5
        return await self.base_generator.get_item_list(**kwargs)

