import tel_consts as tc
from generators.tel_custom_generator import CustomGenerator
from generators.tel_answers_generator import get_doc_with_notes, AnswersGenerator, get_json_params
from telegram import InlineKeyboardButton


class CoordinationsGenerator(CustomGenerator):
    def __init__(self, base_generator: AnswersGenerator):
        super().__init__(base_generator)
        self.base_generator.proc_list.update(
            {tc.TEL_COORDINATION: self.get_coordination,
             tc.TEL_AGREE_COORDINATION: self.get_agree_coordination,
             tc.TEL_DISAGREE_COORDINATION: self.get_agree_coordination,
             tc.TEL_BACK_COORDINATION: self.get_agree_coordination, })

    # вызов документа
    async def try_call_by_id(self, ident, **kwargs):
        if ident == tc.TEL_COORDINATION_ID:
            return await self.get_coordination(tc.TEL_COORDINATION, _id=kwargs['_id'], login=kwargs['login'])
        else:
            return None

    # документ
    async def get_coordination(self, ident, **kwargs):
        keyboard_items = \
            [

                [
                    ["✅ Согласовано", {"ident": tc.TEL_AGREE_COORDINATION,
                                       "_id": kwargs["_id"],
                                       "_type": tc.TEL_COORDINATION_ID}],
                    ["❌ Отклонено", {"ident": tc.TEL_DISAGREE_COORDINATION,
                                     "_id": kwargs["_id"],
                                     "_type": tc.TEL_COORDINATION_ID}],
                    ["↩ На доработку", {"ident": tc.TEL_BACK_COORDINATION,
                                        "_id": kwargs["_id"],
                                        "_type": tc.TEL_COORDINATION_ID}],
                ],
                [
                    ["📁 Файлы", {"ident": tc.TEL_FILES, "_id": kwargs["_id"],
                                 "_type": tc.TEL_COORDINATION_ID}],
                    ["🖋 Визы", {"ident": tc.TEL_VISA, "_id": kwargs["_id"],
                                "_type": tc.TEL_COORDINATION_ID}],
                    ["👀 Кто смотрел", {"ident": tc.TEL_READED,
                                       "_id": kwargs["_id"],
                                       "_type": tc.TEL_COORDINATION_ID}],
                ],
                [
                    ["📝 Документы", {"ident": tc.TEL_NEW_COORDINATIONS}],
                ]

            ]

        frame = await self.base_generator.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0]
            text = get_doc_with_notes(text, frame)
            if not frame['IsCoord'][0]:
                keyboard_items.pop(0)
            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    # визируем документ
    async def get_agree_coordination(self, ident, **kwargs):
        # помечаем прочитанной
        await self.base_generator.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Счета"
        return await self.base_generator.get_item_list(tc.TEL_NEW_COORDINATIONS, login=kwargs['login'])
