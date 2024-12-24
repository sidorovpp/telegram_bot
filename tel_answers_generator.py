import datetime

import tel_consts as tc
import json
from telegram import InlineKeyboardButton
from sql_generator import SQLGenerator
from sql_execute import SQLExecuter
from tel_menu import Menu
# from inn import get_inn

import requests


# упаковка стандартных параметров в JSON строку
def get_json_params(ident, _id=0, _type=0, ext=0, custom=0):
    d = dict()
    d['ident'] = ident
    if _id != 0:
        d['_id'] = _id
    if _type != 0:
        d['_type'] = _type
    if ext != 0:
        d['ext'] = ext
    if custom != 0:
        d['custom'] = custom
    return json.dumps(d)


# добавление параметров из JSON
def parse_params(ident, **kwargs):
    # считываем параметры
    params = json.loads(ident)
    # добавляем параметры, переданные дополнительно
    for k in kwargs:
        if k not in params:
            params[k] = kwargs[k]
    return params


# замена символов для тагов внутри текста, чтобы не ломать html разметку
def replace_symbols(text: str):
    if text:
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
    return text


# подмена параметров
# не использую format_map, потому что в тексте может быть что-то с фигурными скобками
def replace_params(text: str, params: dict):
    for key in params:
        text = text.replace('{' + key + '}', params[key])
    return text


# переписка  документу
def get_doc_with_notes(format_str, frame):
    text = format_str
    if not frame.empty:
        if frame['NoteUser'][0] is not None:
            for i, row in frame.iterrows():
                text = text + '\n\n<b>{NoteUser}</b>  <i>{NoteDate}</i>\n{NoteText}'.format(
                    NoteUser=row['NoteUser'],
                    NoteText=replace_symbols(row['NoteText']),
                    NoteDate=row['NoteDate'],
                )
    return text


class AnswersGenerator:
    sql_executor: SQLExecuter

    def __init__(self):
        self.SG = SQLGenerator()
        self.menu = Menu()

        self.proc_list = {
            tc.TEL_USERS: self.get_frame,
            tc.TEL_VISA: self.get_visa,
            tc.TEL_NOTE: self.get_note,
            tc.TEL_READED: self.get_readed,

            tc.TEL_NEW_TASKS: self.get_item_list,
            tc.TEL_TASKS_UNREADED: self.get_tasks_unreaded,
            tc.TEL_TASKS_FROM_ME: self.get_tasks_from_me,
            tc.TEL_TASKS_TO_ME: self.get_tasks_to_me,
            tc.TEL_TASK: self.get_task,
            tc.TEL_READ_TASK: self.get_read_task,
            tc.TEL_GET_LINKED_DISPOSALS: self.get_item_list,

            tc.TEL_NEW_ACCOUNTS: self.get_item_list,
            tc.TEL_ACCOUNT: self.get_account,
            tc.TEL_AGREE_ACCOUNT: self.get_agree_account,
            tc.TEL_DISAGREE_ACCOUNT: self.get_agree_account,
            tc.TEL_IGNORE_ACCOUNT: self.get_agree_account,

            tc.TEL_NEW_COORDINATIONS: self.get_item_list,
            tc.TEL_COORDINATION: self.get_coordination,
            tc.TEL_AGREE_COORDINATION: self.get_agree_coordination,
            tc.TEL_DISAGREE_COORDINATION: self.get_agree_coordination,
            tc.TEL_BACK_COORDINATION: self.get_agree_coordination,

            tc.TEL_PETITIONS: self.get_item_list,
            tc.TEL_PETITION: self.get_petition,
            tc.TEL_PETITIONS_DSRIM: self.get_petitions_dsrim,
            tc.TEL_PETITIONS_BACK: self.get_petitions_back,
            tc.TEL_PETITIONS_DISAGREE: self.get_petitions_disagree,
            tc.TEL_PETITIONS_MY: self.get_petitions_my,
            tc.TEL_PETITIONS_DIR: self.get_petitions_dir,

            tc.TEL_DOCUMENTS: self.get_item_list,
            tc.TEL_DOCUMENT: self.get_document,

            tc.TEL_CLIENTS: self.get_item_list,
            tc.TEL_CLIENT: self.get_client,
            tc.TEL_CONTR_CLIENTS: self.get_item_list,
            tc.TEL_CONTR_CLIENT: self.get_contr_client,
            tc.TEL_CLIENT_SCORING: self.get_client_scoring,
            # tc.TEL_INN_REQUEST: self.get_inn_request,

            tc.TEL_NOTIFICATIONS: self.get_notifications,
            tc.TEL_READ_NOTIFY: self.get_read_notify,

            tc.TEL_FILES: self.get_files,

            tc.TEL_SET_VISA: self.get_set_visa,

            tc.TEL_SPECIFICATION: self.get_specification,

            tc.TEL_SHOW_SHEETS: self.get_show_sheets,
            tc.TEL_SHOW_SHEET: self.get_show_sheet,
        }

    async def exec_empty(self, ident, **kwargs):
        return await self.sql_executor.exec_empty(self.SG.get_sql_text(ident, **kwargs))

    async def get_data_frame(self, ident, **kwargs):
        return await self.sql_executor.exec(self.SG.get_sql_text(ident, **kwargs))

    async def add_menu(self, ident, table_id, ext_items, **kwargs):
        # ищем меню
        index = self.menu.get_menu(
            ident=tc.TEL_VISA_MENU + '_' + ident,
            login=kwargs['login'],
            ext_items=ext_items)

        if not index:
            # загружаем меню виз
            kwargs['_type'] = table_id
            index = self.menu.add_menu(
                ident=tc.TEL_VISA_MENU + '_' + ident,
                frame=await self.get_frame(tc.TEL_VISA_MENU, **kwargs),
                login=kwargs['login'],
                ext_items=ext_items)

        return index

    # генерируем ответ по идентификатору
    async def get_answer(self, ident, **kwargs):
        params = parse_params(ident, **kwargs)
        if params['ident'] in self.proc_list.keys():
            return await self.proc_list[params['ident']](**params)
        else:
            return await self.get_default(**params)

    # получения фрэйма без дополнительных обработок
    async def get_frame(self, ident, **kwargs):
        frame = await self.get_data_frame(ident, **kwargs)
        return frame

    # стандартный обработчик - просто текст
    async def get_default(self, ident, **kwargs):
        frame = await self.get_data_frame(ident, **kwargs)
        text = ''
        if not frame.empty:
            for i, row in frame.iterrows():
                for k in row:
                    s = '' if not k else k
                    text = text + '\n' + s
                    text = text.strip()
                text = text + '\n\n'
        return text, [], []

    # получаем список файлов
    async def get_files(self, ident, **kwargs):
        files = []
        frame = await self.get_frame(ident, **kwargs)
        if not frame.empty:
            for i, row in frame.iterrows():
                files.append({'_id': row['_id'],
                              'FileName': row['FileName'],
                              'TelegramIdent': row['TelegramIdent'],
                              'Description': replace_symbols(row['Description'])})
        match kwargs['_type']:
            case tc.TEL_TASK_ID:
                text = 'Файлов по задаче найдено: ' + str(len(files))
            case tc.TEL_ACCOUNT_ID:
                text = 'Файлов по счёту найдено: ' + str(len(files))
            case tc.TEL_PETITION_ID:
                text = 'Файлов по заявке найдено: ' + str(len(files))
            case tc.TEL_COORDINATION_ID:
                text = 'Файлов по документу найдено: ' + str(len(files))
            case tc.TEL_DOCUMENT_ID:
                text = 'Файлов по регламенту найдено: ' + str(len(files))
            case _:
                text = 'Файлов найдено: ' + str(len(files))
        return text, [], files

    # получает список элементов и формирует кнопки для списка
    async def get_item_list(self, ident, **kwargs):
        frame = await self.get_data_frame(ident, **kwargs)
        text = 'Найдено {name}: {len}'.format(len=len(frame.index), name=tc.map_actions[ident][1])
        keyboard = []
        for i, row in frame.iterrows():
            info = replace_params(row['Info'], tc.img_lib)
            keyboard.append([
                InlineKeyboardButton('{Info}'.format(
                    Info=info,
                ),
                    callback_data=get_json_params(
                        ident=tc.map_actions[ident][0],
                        _id=row['_id']))
            ])
        return text, keyboard, []

    # информация по задаче
    async def get_task(self, ident, **kwargs):
        # загружаем меню
        index = await self.add_menu(ident, tc.TEL_TASK_ID,
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
        frame = await self.get_data_frame(ident, **kwargs)
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
        await self.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Задачи"
        return await self.get_item_list(tc.TEL_NEW_TASKS, login=kwargs['login'])

    # пишем переписку
    async def get_note(self, ident, **kwargs):
        # помечаем прочитанной
        await self.exec_empty(ident, **kwargs)
        match kwargs['_type']:
            case tc.TEL_TASK_ID:
                return await self.get_task(tc.TEL_TASK, _id=kwargs['_id'], login=kwargs['login'])
            case tc.TEL_ACCOUNT_ID:
                return await self.get_account(tc.TEL_ACCOUNT, _id=kwargs['_id'], login=kwargs['login'])
            case tc.TEL_COORDINATION_ID:
                return await self.get_coordination(tc.TEL_COORDINATION, _id=kwargs['_id'], login=kwargs['login'])
            case tc.TEL_PETITION_ID:
                return await self.get_petition(tc.TEL_PETITION, _id=kwargs['_id'], login=kwargs['login'])
            case tc.TEL_CLIENT_ID:
                return await self.get_petition(tc.TEL_CLIENT, _id=kwargs['_id'], login=kwargs['login'])
            case tc.TEL_SHOW_SHEET_ID:
                # получаем клиента
                frame = await self.get_frame(tc.TEL_GET_CLIENT_FROM_SHOW_SHEET, _id=kwargs['_id'])
                # запоминаем id
                _id = kwargs['_id']
                # подменяем на данные клиента
                kwargs['_type'] = tc.TEL_CLIENT_ID
                kwargs['_id'] = frame['client_id'][0]
                # пишем также в клиента
                await self.exec_empty(ident, **kwargs)
                return await self.get_show_sheet(tc.TEL_SHOW_SHEET, _id=_id, login=kwargs['login'])

    # визируем счёт
    async def get_agree_account(self, ident, **kwargs):
        # помечаем прочитанной
        await self.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Счета"
        return await self.get_item_list(tc.TEL_NEW_ACCOUNTS, login=kwargs['login'])

    # информация по счёту
    async def get_account(self, ident, **kwargs):
        # загружаем меню
        index = await self.add_menu(ident, tc.TEL_ACCOUNT_ID,
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

        frame = await self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0]
            text = get_doc_with_notes(text, frame)

            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    async def get_tasks_unreaded(self, **kwargs):
        kwargs['ident'] = tc.TEL_NEW_TASKS
        kwargs['mode'] = 1
        return await self.get_item_list(**kwargs)

    async def get_tasks_from_me(self, **kwargs):
        kwargs['ident'] = tc.TEL_NEW_TASKS
        kwargs['mode'] = 2
        return await self.get_item_list(**kwargs)

    async def get_tasks_to_me(self, **kwargs):
        kwargs['ident'] = tc.TEL_NEW_TASKS
        kwargs['mode'] = 3
        return await self.get_item_list(**kwargs)

    # список уведомлений
    async def get_notifications(self, ident, **kwargs):

        # ищем идентификатор для кнопки "Посмотреть"
        def get_ident(object_id):
            r = None
            if object_id in tc.map_ids.keys():
                r = tc.map_ids[object_id][0]
            return r

        frame = await self.get_data_frame(ident, login=kwargs['login'], date=kwargs['date'])
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
        await self.exec_empty(ident, _id=_id, login=kwargs['login'])

    # список установленных виз
    async def get_visa(self, ident, _id, **kwargs):
        frame = await self.get_data_frame(ident, _id=_id, **kwargs)
        keyboard = []
        text = ''
        if not frame.empty:
            for i, row in frame.iterrows():
                text = text + '\n<b>{FIO}</b>:  <i>{Visa}</i>'.format(
                    FIO=row['FIO'],
                    Visa=row['Visa'],
                )
        else:
            text = 'Ещё не завизировано'
        return text, keyboard, []

    # список прочитавших
    async def get_readed(self, ident, _id, **kwargs):
        frame = await self.get_data_frame(ident, _id=_id, **kwargs)
        keyboard = []
        text = ''
        if not frame.empty:
            for i, row in frame.iterrows():
                text = text + '\n<i>{Date}</i>  <b>{FIO}</b>'.format(
                    FIO=row['FIO'],
                    Date=row['Date'],
                )
        else:
            text = 'Никто не читал'
        return text, keyboard, []

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

        frame = await self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
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
        await self.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Счета"
        return await self.get_item_list(tc.TEL_NEW_COORDINATIONS, login=kwargs['login'])

    # регламентный документ
    async def get_document(self, ident, **kwargs):
        frame = await self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0]
            text = get_doc_with_notes(text, frame)
            keyboard = [
                [
                    InlineKeyboardButton("Файлы",
                                         callback_data=get_json_params(
                                             ident=tc.TEL_FILES,
                                             _id=kwargs['_id'],
                                             _type=tc.TEL_DOCUMENT_ID
                                         )),
                ]]

            return text, keyboard, []

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
        frame = await self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
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
        frame = await self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
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
            frame = await self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
            text = frame['Info'][0].format_map(tc.img_lib)
            return text, [], []

    # запрашиваем ИНН на сайте налоговой по параметрам клиента
    # async def get_inn_request(self, ident, **kwargs):
    #     frame = await self.get_data_frame(tc.TEL_CLIENT_DATA, _id=kwargs['_id'])
    #     inn = await get_inn(frame)
    #     return inn, [], []

    # устанавливаем визу
    async def get_set_visa(self, ident, **kwargs):
        await self.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'], _type=kwargs['_type'], ext=kwargs['ext'])
        if kwargs['ext'] == -1:
            return 'Подписано', [], []
        else:
            return 'Виза установлена', [], []

    # заявка
    async def get_petition(self, ident, **kwargs):
        # загружаем меню
        index = await self.add_menu(ident, tc.TEL_PETITION_ID,
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

        frame = await self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0].format_map(tc.img_lib)
            text = get_doc_with_notes(text, frame)
            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    async def get_petitions_dsrim(self, **kwargs):
        kwargs['ident'] = tc.TEL_PETITIONS
        kwargs['mode'] = 1
        return await self.get_item_list(**kwargs)

    async def get_petitions_back(self, **kwargs):
        kwargs['ident'] = tc.TEL_PETITIONS
        kwargs['mode'] = 2
        return await self.get_item_list(**kwargs)

    async def get_petitions_disagree(self, **kwargs):
        kwargs['ident'] = tc.TEL_PETITIONS
        kwargs['mode'] = 3
        return await self.get_item_list(**kwargs)

    async def get_petitions_my(self, **kwargs):
        kwargs['ident'] = tc.TEL_PETITIONS
        kwargs['mode'] = 4
        return await self.get_item_list(**kwargs)

    async def get_petitions_dir(self, **kwargs):
        kwargs['ident'] = tc.TEL_PETITIONS
        kwargs['mode'] = 5
        return await self.get_item_list(**kwargs)

    # спецификация
    async def get_specification(self, ident, **kwargs):
        frame = await self.get_data_frame(ident, text=kwargs['text'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0].format_map(tc.img_lib)
        else:
            text = 'Спецификация не найдена'
        return text, [], []

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
        res = await self.get_item_list(**kwargs)
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

    async def get_show_sheet(self, ident, **kwargs):
        frame = await self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
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


answers_generator = AnswersGenerator()
