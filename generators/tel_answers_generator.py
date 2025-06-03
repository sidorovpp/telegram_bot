import tel_consts as tc
import json
from telegram import InlineKeyboardButton
from sql_generator import SQLGenerator
from sql_execute import SQLExecuter
from tel_menu import Menu


# from inn import get_inn


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


# базовый генератор ответов
class AnswersGenerator:
    sql_executor: SQLExecuter

    def __init__(self):
        self.SG = SQLGenerator()
        self.menu = Menu()
        self.generators = []

        default_list = [
            tc.TEL_NEW_TASKS,
            tc.TEL_NEW_ACCOUNTS,
            tc.TEL_NEW_COORDINATIONS,
            tc.TEL_PETITIONS,
            tc.TEL_DOCUMENTS,
            tc.TEL_CLIENTS,
            tc.TEL_CONTR_CLIENTS,
            tc.TEL_GET_LINKED_DISPOSALS,
            ]
        # добавляем универсальный обработчик get_item_list для списков
        self.proc_list = {item: self.get_item_list for item in default_list}
        # получение данных по пользователям для уведомлений
        self.proc_list.update({tc.TEL_USERS: self.get_frame})

    # добавление генератора
    def add_custom_generator(self, generator_class):
        self.generators.append(generator_class(self))

    # выполнение sql без результата
    async def exec_empty(self, ident, **kwargs):
        return await self.sql_executor.exec_empty(self.SG.get_sql_text(ident, **kwargs))

    # выполнение sql с данными
    async def get_data_frame(self, ident, **kwargs):
        return await self.sql_executor.exec(self.SG.get_sql_text(ident, **kwargs))

    # добавление меню с визами
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


answers_generator = AnswersGenerator()
