import tel_consts
import json
from telegram import InlineKeyboardButton


def get_json_params(ident, _id=0, _type=0, ext=0):
    d = dict()
    d['ident'] = ident
    d['_id'] = _id
    d['_type'] = _type
    d['ext'] = ext
    return json.dumps(d)


def parse_params(ident, **kwargs):
    # считываем параметры
    params = json.loads(ident)
    # добавляем параметры, переданные дополнительно
    for k in kwargs:
        if k not in params:
            params[k] = kwargs[k]
    return params


def replace_symbols(text: str):
    if text:
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
    return text


class AnswersGenerator:
    def __init__(self, sql_executer, sql_generator):
        self.SE = sql_executer
        self.SG = sql_generator

        self.proc_list = {
            tel_consts.TEL_USERS: self.get_frame,
            tel_consts.TEL_VISA: self.get_visa,
            tel_consts.TEL_NOTE: self.get_note,

            tel_consts.TEL_NEW_TASKS: self.get_new_tasks,
            tel_consts.TEL_TASK: self.get_task,
            tel_consts.TEL_READ_TASK: self.get_read_task,

            tel_consts.TEL_NEW_ACCOUNTS: self.get_new_accounts,
            tel_consts.TEL_ACCOUNT: self.get_account,
            tel_consts.TEL_AGREE_ACCOUNT: self.get_agree_account,
            tel_consts.TEL_DISAGREE_ACCOUNT: self.get_agree_account,
            tel_consts.TEL_IGNORE_ACCOUNT: self.get_agree_account,

            tel_consts.TEL_NEW_COORDINATIONS: self.get_new_coordinations,
            tel_consts.TEL_COORDINATION: self.get_coordination,
            tel_consts.TEL_AGREE_COORDINATION: self.get_agree_coordination,
            tel_consts.TEL_DISAGREE_COORDINATION: self.get_agree_coordination,
            tel_consts.TEL_BACK_COORDINATION: self.get_agree_coordination,

            tel_consts.TEL_DOCUMENTS: self.get_documents,
            tel_consts.TEL_DOCUMENT: self.get_document,

            tel_consts.TEL_CLIENTS: self.get_clients,
            tel_consts.TEL_CLIENT: self.get_client,

            tel_consts.TEL_NOTIFICATIONS: self.get_notifications,

            tel_consts.TEL_FILES: self.get_files
        }

    def exec_empty(self, ident, **kwargs):
        return self.SE.exec_empty(self.SG.get_sql_text(ident, **kwargs))

    def get_data_frame(self, ident, **kwargs):
        return self.SE.exec(self.SG.get_sql_text(ident, **kwargs))

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

    # переписка  документу
    def get_doc_with_notes(self, format_str, frame):
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
            case tel_consts.TEL_TASK_ID:
                text = 'Файлов по задаче найдено: ' + str(len(files))
            case tel_consts.TEL_ACCOUNT_ID:
                text = 'Файлов по счёту найдено: ' + str(len(files))
            case tel_consts.TEL_COORDINATION_ID:
                text = 'Файлов по документу найдено: ' + str(len(files))
            case tel_consts.TEL_DOCUMENT_ID:
                text = 'Файлов по регламенту найдено: ' + str(len(files))
        return text, [], files

    # информация по задаче
    def get_task(self, ident, **kwargs):
        keyboard_items = [[
            ["📖 Прочитано", {"ident": tel_consts.TEL_READ_TASK,
                             "_id": kwargs["_id"],
                             "_type": tel_consts.TEL_TASK_ID}],
            ["📁 Файлы", {"ident": tel_consts.TEL_FILES,
                         "_id": kwargs["_id"],
                         "_type": tel_consts.TEL_TASK_ID}],
            ["📓 Задачи", {"ident": tel_consts.TEL_NEW_TASKS}],
        ]]
        frame = self.get_data_frame(ident, **kwargs)
        if not frame.empty:
            text = '<b>{Number}{State}</b>\n{Urgency}\n\n{SenderFirmName}\n' \
                   '<i>{Sender} ➡ {Receiver}</i>\n\n<b>{Theme}</b>\n\n{Zadanie}'.format(
                        Number=frame['Number'][0],
                        Theme=replace_symbols(frame['Theme'][0]),
                        Zadanie=replace_symbols(frame['Zadanie'][0]),
                        Sender=frame['Sender'][0],
                        Receiver=frame['Receiver'][0],
                        Urgency=frame['Urgency'][0] if frame['Urgency_id'][0] != 6 else frame['Urgency'][0] + '❗',
                        State=tel_consts.TEL_TASK_STATES[frame['CurrentState'][0]],
                        SenderFirmName=frame['SenderFirmName'][0],
                    )

            text = self.get_doc_with_notes(text, frame)

            keyboard = [[InlineKeyboardButton(y[0], callback_data=get_json_params(**y[1])) for y in x]
                        for x in keyboard_items]

            return text, keyboard, []

    # читаем задачу
    def get_read_task(self, ident, **kwargs):
        # помечаем прочитанной
        self.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Задачи"
        return self.get_new_tasks(tel_consts.TEL_NEW_TASKS, login=kwargs['login'])

    # пишем переписку
    def get_note(self, ident, **kwargs):
        # помечаем прочитанной
        self.exec_empty(ident, **kwargs)
        match kwargs['_type']:
            case tel_consts.TEL_TASK_ID:
                return self.get_task(tel_consts.TEL_TASK, _id=kwargs['_id'], login=kwargs['login'])
            case tel_consts.TEL_ACCOUNT_ID:
                return self.get_account(tel_consts.TEL_ACCOUNT, _id=kwargs['_id'], login=kwargs['login'])
            case tel_consts.TEL_COORDINATION_ID:
                return self.get_coordination(tel_consts.TEL_COORDINATION, _id=kwargs['_id'], login=kwargs['login'])

    # визируем счёт
    def get_agree_account(self, ident, **kwargs):
        # помечаем прочитанной
        self.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'])
        # вызываем пункт "Счета"
        return self.get_new_accounts(tel_consts.TEL_NEW_ACCOUNTS, kwargs['login'])

    # информация по счёту
    def get_account(self, ident, **kwargs):
        keyboard_items = [[
            ["✅ За", {"ident": tel_consts.TEL_AGREE_ACCOUNT,
                      "_id": kwargs["_id"],
                      "_type": tel_consts.TEL_ACCOUNT_ID}],
            ["❌ Против", {"ident": tel_consts.TEL_DISAGREE_ACCOUNT,
                          "_id": kwargs["_id"],
                          "_type": tel_consts.TEL_ACCOUNT_ID}],
            ["⬆ На усмотрение", {"ident": tel_consts.TEL_IGNORE_ACCOUNT,
                                 "_id": kwargs["_id"],
                                 "_type": tel_consts.TEL_ACCOUNT_ID}],
        ],
            [
                ["📁 Файлы", {"ident": tel_consts.TEL_FILES, "_id": kwargs["_id"], "_type": tel_consts.TEL_ACCOUNT_ID}],
                ["🖋 Визы", {"ident": tel_consts.TEL_VISA, "_id": kwargs["_id"], "_type": tel_consts.TEL_ACCOUNT_ID}],
                ["💸 Счета", {"ident": tel_consts.TEL_NEW_ACCOUNTS}],
            ]]

        frame = self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = '<b>{Number}</b>\n\n<i>{FirmName}</i>\n\n<b>{ClientName}</b>\n\n{Summa}\n\n{Description}'.format(
                Number=frame['Number'][0],
                FirmName=frame['FirmName'][0],
                ClientName=frame['ClientName'][0],
                Summa=frame['Summa'][0],
                Description=replace_symbols(frame['Description'][0]),
            )

            text = self.get_doc_with_notes(text, frame)

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
                    CurrentState=tel_consts.TEL_TASK_STATES[row['CurrentState']],
                    Number=row['Number'],
                    Theme=replace_symbols(row['Theme'])),
                    callback_data=get_json_params(
                        ident=tel_consts.TEL_TASK,
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
                    CurrentState=tel_consts.TEL_ACCOUNT_STATES[row['CurrentState']],
                    Summa=row['Summa'],
                    Number=row['Number'],
                    FirmName=row['FirmName']),
                    callback_data=get_json_params(
                        ident=tel_consts.TEL_ACCOUNT,
                        _id=row['_id']))
            ])
        return text, keyboard, []

    # список уведомлений
    def get_notifications(self, ident, **kwargs):

        # ищем идентификатор для кнопки "Посмотреть"
        def get_ident(object_id):
            r = None
            match object_id:
                case tel_consts.TEL_ACCOUNT_ID:
                    r = tel_consts.TEL_NEW_ACCOUNTS
                case tel_consts.TEL_COORDINATION_ID:
                    r = tel_consts.TEL_NEW_COORDINATIONS
                case tel_consts.TEL_STAFF_ID:
                    r = tel_consts.TEL_STAFF
                case tel_consts.TEL_STAFF_REG_ID:
                    r = tel_consts.TEL_STAFF
                case tel_consts.TEL_ACCOUNT_REG_ID:
                    r = tel_consts.TEL_NEW_ACCOUNTS
                case tel_consts.TEL_CLIENT_ID:
                    r = tel_consts.TEL_CLIENTS
                case tel_consts.TEL_CLIENT_REG_ID:
                    r = tel_consts.TEL_CLIENTS
                case tel_consts.TEL_COORDINATION_REG_ID:
                    r = tel_consts.TEL_NEW_COORDINATIONS
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

    # список новых документов
    def get_new_coordinations(self, ident, login, **kwargs):
        frame = self.get_data_frame(ident, login=login, **kwargs)
        text = 'Найдено документов: {len}'.format(len=len(frame.index))
        keyboard = []
        for i, row in frame.iterrows():
            keyboard.append([
                InlineKeyboardButton('{CurrentState} {Number} {InitFIO} {ClientName} {Theme}'.format(
                    CurrentState=tel_consts.TEL_COORD_STATES[row['CurrentState']],
                    Number=row['Number'],
                    Theme=row['Theme'],
                    InitFIO=row['InitFIO'],
                    ClientName=row['ClientName']),
                    callback_data=get_json_params(ident=tel_consts.TEL_COORDINATION, _id=row['_id']))
            ])
        return text, keyboard, []

    # документ
    def get_coordination(self, ident, **kwargs):
        keyboard_items = [[
            ["✅ Согласовано", {"ident": tel_consts.TEL_AGREE_COORDINATION,
                               "_id": kwargs["_id"],
                               "_type": tel_consts.TEL_COORDINATION_ID}],
            ["❌ Отклонено", {"ident": tel_consts.TEL_DISAGREE_COORDINATION,
                             "_id": kwargs["_id"],
                             "_type": tel_consts.TEL_COORDINATION_ID}],
            ["↩ На доработку", {"ident": tel_consts.TEL_BACK_COORDINATION,
                                "_id": kwargs["_id"],
                                "_type": tel_consts.TEL_COORDINATION_ID}],
        ],
            [
                ["📁 Файлы", {"ident": tel_consts.TEL_FILES, "_id": kwargs["_id"],
                             "_type": tel_consts.TEL_COORDINATION_ID}],
                ["🖋 Визы", {"ident": tel_consts.TEL_VISA, "_id": kwargs["_id"],
                            "_type": tel_consts.TEL_COORDINATION_ID}],
                ["📝 Документы", {"ident": tel_consts.TEL_NEW_COORDINATIONS}],
            ]]

        frame = self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = '<b>{Number}</b>\n\n<i>{Theme}</i>\n\n<b>' \
                   '{ClientName}</b>\n\n<b>{InitFIO}</b>\n\n{Summa}\n\n{DocText}'.format(
                        Number=frame['Number'][0],
                        Theme=frame['Theme'][0],
                        ClientName=frame['ClientName'][0],
                        Summa=frame['Summa'][0],
                        DocText=replace_symbols(frame['DocText'][0]),
                        InitFIO=frame['InitFIO'][0]
                    )
            text = self.get_doc_with_notes(text, frame)
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
        return self.get_new_coordinations(tel_consts.TEL_NEW_COORDINATIONS, kwargs['login'])

    # список новых документов
    def get_documents(self, ident, login, **kwargs):
        frame = self.get_data_frame(ident, login=login, **kwargs)
        text = 'Найдено регламентов: {len}'.format(len=len(frame.index))
        keyboard = []
        for i, row in frame.iterrows():
            keyboard.append([
                InlineKeyboardButton(row['Code'] + ' ' +
                                     row['Description'],
                                     callback_data=get_json_params(ident=tel_consts.TEL_DOCUMENT, _id=row['_id']))
            ])
        return text, keyboard, []

    # документ
    def get_document(self, ident, **kwargs):
        frame = self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = '<b>{Code}</b>\n\n<i>{GroupName}</i>\n\n<i>' \
                   '{TypeName}</i>\n\n<b>{Description}</b>'.format(
                        Code=frame['Code'][0],
                        GroupName=frame['GroupName'][0],
                        TypeName=frame['TypeName'][0],
                        Description=replace_symbols(frame['Description'][0]),
                    )
            text = self.get_doc_with_notes(text, frame)
            keyboard = [
                [
                    InlineKeyboardButton("Файлы",
                                         callback_data=get_json_params(
                                             ident=tel_consts.TEL_FILES,
                                             _id=kwargs['_id'],
                                             _type=tel_consts.TEL_DOCUMENT_ID
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
                                     callback_data=get_json_params(ident=tel_consts.TEL_CLIENT, _id=row['_id']))
            ])
        return text, keyboard, []

    # документ
    def get_client(self, ident, **kwargs):
        frame = self.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
        if not frame.empty:
            text = '<b>{FIO}</b>\n\n<i>{MainPhone}</i>\n\n<i>' \
                   '{AdditionalPhone}</i>'.format(
                        FIO=frame['FIO'][0],
                        MainPhone=frame['MainPhone'][0],
                        AdditionalPhone=frame['AdditionalPhone'][0],
                    )
            text = self.get_doc_with_notes(text, frame)
            keyboard = [
                [
                    InlineKeyboardButton("Файлы",
                                         callback_data=get_json_params(
                                             ident=tel_consts.TEL_FILES,
                                             _id=kwargs['_id'],
                                             _type=tel_consts.TEL_CLIENT_ID
                                         )),
                ]]

            return text, keyboard, []
