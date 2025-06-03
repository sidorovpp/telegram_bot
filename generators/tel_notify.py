import tel_consts as tc
from generators.tel_custom_generator import CustomGenerator
from generators.tel_answers_generator import AnswersGenerator, get_json_params
from telegram import InlineKeyboardButton


class NotifyGenerator(CustomGenerator):
    def __init__(self, base_generator: AnswersGenerator):
        super().__init__(base_generator)
        self.base_generator.proc_list.update(
            {
                tc.TEL_NOTIFICATIONS: self.get_notifications,
                tc.TEL_READ_NOTIFY: self.get_read_notify,
            })

    # список уведомлений
    async def get_notifications(self, ident, **kwargs):

        # ищем идентификатор для кнопки "Посмотреть"
        def get_ident(object_id):
            r = None
            if object_id in tc.map_ids.keys():
                r = tc.map_ids[object_id][0]
            return r

        frame = await self.base_generator.get_data_frame(ident, login=kwargs['login'], date=kwargs['date'])
        res = []
        if len(frame.index) > 0:
            for i, row in frame.iterrows():
                ident = get_ident(row['Object_id'])
                s = '<b>{Date}</b>\n{Text}'.format(
                    Date=row['Date'],
                    Text=row['Text'])
                if ident:
                    keyboard_items = \
                        [
                            [
                                ["🔍 Посмотреть", {"ident": ident, "ext": row['_id']}],
                                ["📖 Прочитано", {"ident": tc.TEL_READ_NOTIFY, "_id": row['_id']}]
                            ]
                        ]
                else:
                    keyboard_items = \
                        [
                            [
                                ["📖 Прочитано", {"ident": tc.TEL_READ_NOTIFY, "_id": row['_id']}]
                            ]
                        ]
                keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                            for x in keyboard_items]
                res.append((s, keyboard, []))
        return res

    # ставим уведомлению прочитанность
    async def get_read_notify(self, ident, _id, **kwargs):
        await self.base_generator.exec_empty(ident, _id=_id, login=kwargs['login'])
