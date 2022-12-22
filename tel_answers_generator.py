import tel_consts as tc
import json
from telegram import InlineKeyboardButton
from sql_generator import SQLGenerator
from sql_execute import SQLExecuter


# упаковка стандартных параметров в JSON строку
def get_json_params(ident, _id=0, _type=0, ext=0):
    d = dict()
    d['ident'] = ident
    d['_id'] = _id
    d['_type'] = _type
    d['ext'] = ext
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

        self.proc_list = {
            tc.TEL_USERS: self.get_frame,
            tc.TEL_VISA: self.get_visa,
            tc.TEL_NOTE: self.get_note,
            tc.TEL_READED: self.get_readed,

            tc.TEL_NEW_TASKS: self.get_new_tasks,
            tc.TEL_TASK: self.get_task,
            tc.TEL_READ_TASK: self.get_read_task,

            tc.TEL_NEW_ACCOUNTS: self.get_new_accounts,
            tc.TEL_ACCOUNT: self.get_account,
            tc.TEL_AGREE_ACCOUNT: self.get_agree_account,
            tc.TEL_DISAGREE_ACCOUNT: self.get_agree_account,
            tc.TEL_IGNORE_ACCOUNT: self.get_agree_account,

            tc.TEL_NEW_COORDINATIONS: self.get_new_coordinations,
            tc.TEL_COORDINATION: self.get_coordination,
            tc.TEL_AGREE_COORDINATION: self.get_agree_coordination,
            tc.TEL_DISAGREE_COORDINATION: self.get_agree_coordination,
            tc.TEL_BACK_COORDINATION: self.get_agree_coordination,

            tc.TEL_DOCUMENTS: self.get_documents,
            tc.TEL_DOCUMENT: self.get_document,

            tc.TEL_CLIENTS: self.get_clients,
            tc.TEL_CLIENT: self.get_client,

            tc.TEL_NOTIFICATIONS: self.get_notifications,

            tc.TEL_FILES: self.get_files,
        }

    def exec_empty(self, ident, **kwargs):
        return self.sql_executor.exec_empty(self.SG.get_sql_text(ident, **kwargs))

    def get_data_frame(self, ident, **kwargs):
        return self.sql_executor.exec(self.SG.get_sql_text(ident, **kwargs))

    # генерируем ответ по идентификатору
    def get_answer(self, ident, **kwargs):
        params = parse_params(ident, **kwargs)
        if params['ident'] in self.proc_list.keys():
            return self.proc_list[params['ident']](**params)
        else:
            return self.get_default(**params)

    # получения фрэйме без дополнительных обработок
    def get_frame(self, ident, **kwargs):
        frame = self.get_data_frame(ident, **kwargs)
        return frame

    # стандартный обработчик - просто текст
    def get_default(self, ident, **kwargs):
        frame = self.get_data_frame(ident, **kwargs)
        text = ''
        if not frame.empty:
            for i, row in frame.iterrows():
                for k in row:
                    text = text + '\n' + k
                    text = text.strip()
                text = text + '\n\n'
        return text, [], []

    # получаем список файлов
    def get_files(self, ident, **kwargs):
        files = []
        frame = self.get_frame(ident, **kwargs)
        if not frame.empty:
            for i, row in frame.iterrows():
                files.append({'_id': row['_id'],
                              'FileName': row['FileName'],
                              'TelegramIdent': row['TelegramIdent'],
                              'Description': replace_symbols(row['Description'])})
        text = ''
        match kwargs['_type']:
            case tc.TEL_TASK_ID:
                text = 'Файлов по задаче найдено: ' + str(len(files))
            case tc.TEL_ACCOUNT_ID:
                text = 'Файлов по счёту найдено: ' + str(len(files))
            case tc.TEL_COORDINATION_ID:
                text = 'Файлов по документу найдено: ' + str(len(files))
            case tc.TEL_DOCUMENT_ID:
                text = 'Файлов по регламенту найдено: ' + str(len(files))
        return text, [], files

    # информация по задаче
    def get_task(self, ident, **kwargs):
        keyboard_items = \
            [
                [
                    ["📖 Прочитано", {"ident": tc.TEL_READ_TASK,
                                     "_id": kwargs["_id"],
                                     "_type": tc.TEL_TASK_ID}],
                    ["📁 Файлы", {"ident": tc.TEL_FILES,
                                 "_id": kwargs["_id"],
                                 "_type": tc.TEL_TASK_ID}],
                    ["👀 Кто смотрел", {"ident": tc.TEL_READED,
                                       "_id": kwargs["_id"],
                                       "_type": tc.TEL_TASK_ID}],
                ],
                [
                    ["📓 Задачи", {"ident": tc.TEL_NEW_TASKS}],
                ]
            ]
        frame = self.get_data_frame(ident, **kwargs)
        if not frame.empty:
            urg = '❗' if frame['UrgencyID'][0] == 6 else ''
            text = tc.TEL_TASK_STATES[frame['CurrentStateID'][0]] + urg + frame['Info'][0]
            text = get_doc_with_notes(text, frame)

            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    # читаем задачу
    def get_read_task(self, ident, **kwargs):
        # помечаем прочитанной
        self.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Задачи"
        return self.get_new_tasks(tc.TEL_NEW_TASKS, login=kwargs['login'])

    # пишем переписку
    def get_note(self, ident, **kwargs):
        # помечаем прочитанной
        self.exec_empty(ident, **kwargs)
        match kwargs['_type']:
            case tc.TEL_TASK_ID:
                return self.get_task(tc.TEL_TASK, _id=kwargs['_id'], login=kwargs['login'])
            case tc.TEL_ACCOUNT_ID:
                return self.get_account(tc.TEL_ACCOUNT, _id=kwargs['_id'], login=kwargs['login'])
            case tc.TEL_COORDINATION_ID:
                return self.get_coordination(tc.TEL_COORDINATION, _id=kwargs['_id'], login=kwargs['login'])

    # визируем счёт
    def get_agree_account(self, ident, **kwargs):
        # помечаем прочитанной
        self.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Счета"
        return self.get_new_accounts(tc.TEL_NEW_ACCOUNTS, kwargs['login'])

    # информация по счёту
    def get_account(self, ident, **kwargs):
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
                ]
            ]

        frame = self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0]
            text = get_doc_with_notes(text, frame)

            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    # список новых задач
    def get_new_tasks(self, ident, **kwargs):
        frame = self.get_data_frame(ident, **kwargs)
        text = 'Найдено задач: {len}'.format(len=len(frame.index))
        keyboard = []
        for i, row in frame.iterrows():
            keyboard.append([
                InlineKeyboardButton('{CurrentState}{Number} - {Theme}'.format(
                    CurrentState=tc.TEL_TASK_STATES[row['CurrentState']],
                    Number=row['Number'],
                    Theme=replace_symbols(row['Theme'])),
                    callback_data=get_json_params(
                        ident=tc.TEL_TASK,
                        _id=row['_id']))
            ])
        return text, keyboard, []

    # список новых счетов
    def get_new_accounts(self, ident, login, **kwargs):
        frame = self.get_data_frame(ident, login=login, **kwargs)
        text = 'Найдено счетов: {len}'.format(len=len(frame.index))
        keyboard = []
        for i, row in frame.iterrows():
            keyboard.append([
                InlineKeyboardButton('{CurrentState}{Number} {FirmName} {Summa}'.format(
                    CurrentState=tc.TEL_ACCOUNT_STATES[row['CurrentState']],
                    Summa=row['Summa'],
                    Number=row['Number'],
                    FirmName=row['FirmName']),
                    callback_data=get_json_params(
                        ident=tc.TEL_ACCOUNT,
                        _id=row['_id']))
            ])
        return text, keyboard, []

    # список уведомлений
    def get_notifications(self, ident, **kwargs):

        # ищем идентификатор для кнопки "Посмотреть"
        def get_ident(object_id):
            r = None
            match object_id:
                case tc.TEL_ACCOUNT_ID:
                    r = tc.TEL_NEW_ACCOUNTS
                case tc.TEL_COORDINATION_ID:
                    r = tc.TEL_NEW_COORDINATIONS
                case tc.TEL_STAFF_ID:
                    r = tc.TEL_STAFF
                case tc.TEL_STAFF_REG_ID:
                    r = tc.TEL_STAFF
                case tc.TEL_ACCOUNT_REG_ID:
                    r = tc.TEL_NEW_ACCOUNTS
                case tc.TEL_CLIENT_ID:
                    r = tc.TEL_CLIENTS
                case tc.TEL_CLIENT_REG_ID:
                    r = tc.TEL_CLIENTS
                case tc.TEL_COORDINATION_REG_ID:
                    r = tc.TEL_NEW_COORDINATIONS
                case tc.TEL_TASK_REG_ID:
                    r = tc.TEL_NEW_TASKS
            return r

        frame = self.get_data_frame(ident, login=kwargs['login'], date=kwargs['date'])
        text = ''
        res = []
        if len(frame.index) > 0:
            for i, row in frame.iterrows():
                ident = get_ident(row['Object_id'])
                if ident:
                    s = '<b>{Date}</b>\n{Text}'.format(
                        Date=row['Date'],
                        Text=row['Text'])  # replace_symbols(row['Text'])) не подменяю разметку в уведомлениях

                    res.append(
                        (s,
                         [
                             [InlineKeyboardButton("🔍 Посмотреть",
                                                   callback_data=get_json_params(
                                                       ident=ident,
                                                       ext=row['_id']))]
                         ],
                         []
                         ))
                else:
                    text = text + '\n\n<b>{Date}</b>\n{Text}'.format(
                        Date=row['Date'],
                        Text=row['Text'],
                    )
            if text != '':
                res.append((text, [], []))
        return res

    # список установленных виз
    def get_visa(self, ident, _id, **kwargs):
        frame = self.get_data_frame(ident, _id=_id, **kwargs)
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

    # список установленных виз
    def get_readed(self, ident, _id, **kwargs):
        frame = self.get_data_frame(ident, _id=_id, **kwargs)
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

    # список новых документов
    def get_new_coordinations(self, ident, login, **kwargs):
        frame = self.get_data_frame(ident, login=login, **kwargs)
        text = 'Найдено документов: {len}'.format(len=len(frame.index))
        keyboard = []
        for i, row in frame.iterrows():
            keyboard.append([
                InlineKeyboardButton('{CurrentState} {Number} {InitFIO} {ClientName} {Theme}'.format(
                    CurrentState=tc.TEL_COORD_STATES[row['CurrentState']],
                    Number=row['Number'],
                    Theme=row['Theme'],
                    InitFIO=row['InitFIO'],
                    ClientName=row['ClientName']),
                    callback_data=get_json_params(ident=tc.TEL_COORDINATION, _id=row['_id']))
            ])
        return text, keyboard, []

    # документ
    def get_coordination(self, ident, **kwargs):
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

        frame = self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0]
            text = get_doc_with_notes(text, frame)
            if not frame['IsCoord'][0]:
                keyboard_items.pop(0)
            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    # визируем документ
    def get_agree_coordination(self, ident, **kwargs):
        # помечаем прочитанной
        self.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Счета"
        return self.get_new_coordinations(tc.TEL_NEW_COORDINATIONS, kwargs['login'])

    # список новых документов
    def get_documents(self, ident, login, **kwargs):
        frame = self.get_data_frame(ident, login=login, **kwargs)
        text = 'Найдено регламентов: {len}'.format(len=len(frame.index))
        keyboard = []
        for i, row in frame.iterrows():
            keyboard.append([
                InlineKeyboardButton(row['Code'] + ' ' +
                                     row['Description'],
                                     callback_data=get_json_params(ident=tc.TEL_DOCUMENT, _id=row['_id']))
            ])
        return text, keyboard, []

    # документ
    def get_document(self, ident, **kwargs):
        frame = self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
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

    # список клеинтов
    def get_clients(self, ident, login, **kwargs):
        frame = self.get_data_frame(ident, login=login, **kwargs)
        text = 'Найдено клиентов: {len}'.format(len=len(frame.index))
        keyboard = []
        for i, row in frame.iterrows():
            keyboard.append([
                InlineKeyboardButton(row['FIO'] + ' ' +
                                     row['MainPhone'],
                                     callback_data=get_json_params(ident=tc.TEL_CLIENT, _id=row['_id']))
            ])
        return text, keyboard, []

    # документ
    def get_client(self, ident, **kwargs):
        frame = self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = frame['Info'][0]
            text = get_doc_with_notes(text, frame)
            keyboard = [
                [
                    InlineKeyboardButton("Файлы",
                                         callback_data=get_json_params(
                                             ident=tc.TEL_FILES,
                                             _id=kwargs['_id'],
                                             _type=tc.TEL_CLIENT_ID
                                         )),
                ]]

            return text, keyboard, []


answers_generator = AnswersGenerator()
