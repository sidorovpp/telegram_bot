import tel_consts as tc
from generators.tel_custom_generator import CustomGenerator
from generators.tel_answers_generator import replace_params, get_doc_with_notes, AnswersGenerator, get_json_params
from telegram import InlineKeyboardButton


class TasksGenerator(CustomGenerator):
    def __init__(self, base_generator: AnswersGenerator):
        super().__init__(base_generator)
        self.base_generator.proc_list.update(
            {tc.TEL_TASKS_UNREADED: self.get_tasks_unreaded,
             tc.TEL_TASKS_FROM_ME: self.get_tasks_from_me,
             tc.TEL_TASKS_TO_ME: self.get_tasks_to_me,
             tc.TEL_TASK: self.get_task,
             tc.TEL_READ_TASK: self.get_read_task, })

    # вызов задачи
    async def try_call_by_id(self, ident, **kwargs):
        if ident == tc.TEL_TASK_ID:
            return await self.get_task(tc.TEL_TASK, _id=kwargs['_id'], login=kwargs['login'])
        else:
            return None

    # информация по задаче
    async def get_task(self, ident, **kwargs):
        # загружаем меню
        index = await self.base_generator.add_menu(
            ident, tc.TEL_TASK_ID,
            [{"name": "🖋 Визы",
              "_json": '{{"ident": "{ident}", "_id": {_id}, "_type": {_type}}}'.format(
                  ident=tc.TEL_VISA,
                  _id=kwargs["_id"],
                  _type=tc.TEL_TASK_ID)}],
            **kwargs)
        keyboard_items = \
            [
                [
                    ["📖 Прочитано", {"ident": tc.TEL_READ_TASK,
                                     "_id": kwargs["_id"],
                                     "_type": tc.TEL_TASK_ID}],
                    ["📁 Файлы", {"ident": tc.TEL_FILES,
                                 "_id": kwargs["_id"],
                                 "_type": tc.TEL_TASK_ID}],
                ],
                [
                    ["👀 Кто смотрел", {"ident": tc.TEL_READED,
                                       "_id": kwargs["_id"],
                                       "_type": tc.TEL_TASK_ID}],
                    ["⛓ Связанные", {"ident": tc.TEL_GET_LINKED_DISPOSALS,
                                     "_id": kwargs["_id"]
                                     }],

                ],
                [
                    ["📝 Комментарий", {"ident": tc.TEL_NOTE, "_type": tc.TEL_TASK_ID,
                                       "_id": kwargs["_id"]}],
                    ["🖋 Виза/подпись", {"ident": tc.TEL_MENU, "_id": kwargs["_id"], "_type": index, "ext": -1}],
                    ["📓 Задачи", {"ident": tc.TEL_NEW_TASKS}],
                ]
            ]
        frame = await self.base_generator.get_data_frame(ident, **kwargs)
        if not frame.empty:
            # urg = '❗' if frame['UrgencyID'][0] == 6 else ''
            # text = tc.TEL_TASK_STATES[frame['CurrentStateID'][0]] + urg + frame['Info'][0]

            text = replace_params(frame['Info'][0], tc.img_lib)
            text = get_doc_with_notes(text, frame)

            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    # читаем задачу
    # помечаем прочитанной
    async def get_read_task(self, ident, **kwargs):
        await self.base_generator.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Задачи"
        return await self.base_generator.get_item_list(tc.TEL_NEW_TASKS, login=kwargs['login'])

    async def get_tasks_unreaded(self, **kwargs):
        kwargs['ident'] = tc.TEL_NEW_TASKS
        kwargs['mode'] = 1
        return await self.base_generator.get_item_list(**kwargs)

    async def get_tasks_from_me(self, **kwargs):
        kwargs['ident'] = tc.TEL_NEW_TASKS
        kwargs['mode'] = 2
        return await self.base_generator.get_item_list(**kwargs)

    async def get_tasks_to_me(self, **kwargs):
        kwargs['ident'] = tc.TEL_NEW_TASKS
        kwargs['mode'] = 3
        return await self.base_generator.get_item_list(**kwargs)
