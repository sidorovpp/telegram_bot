import tel_consts
import re


class SQLGenerator:
    def __init__(self):
        self.proc_list = {
            tel_consts.TEL_USERS: get_users,
            tel_consts.TEL_START: start,

            tel_consts.TEL_VISA: get_visa,
            tel_consts.TEL_NOTE: note,

            tel_consts.TEL_NEW_TASKS: new_tasks,
            tel_consts.TEL_TASK: get_task,
            tel_consts.TEL_READ_TASK: read_task,

            tel_consts.TEL_NEW_ACCOUNTS: new_accounts,
            tel_consts.TEL_ACCOUNT: get_account,
            tel_consts.TEL_AGREE_ACCOUNT: agree_account,
            tel_consts.TEL_DISAGREE_ACCOUNT: disagree_account,
            tel_consts.TEL_IGNORE_ACCOUNT: ignore_account,

            tel_consts.TEL_NEW_COORDINATIONS: new_coordinations,
            tel_consts.TEL_COORDINATION: get_coordination,
            tel_consts.TEL_AGREE_COORDINATION: agree_coordination,
            tel_consts.TEL_DISAGREE_COORDINATION: disagree_coordination,
            tel_consts.TEL_BACK_COORDINATION: back_coordination,

            tel_consts.TEL_DOCUMENTS: get_documents,
            tel_consts.TEL_DOCUMENT: get_document,

            tel_consts.TEL_CLIENTS: get_clients,
            tel_consts.TEL_CLIENT: get_client,

            tel_consts.TEL_STAFF: get_staff,

            tel_consts.TEL_NOTIFICATIONS: get_notifications,

            tel_consts.TEL_FILES: get_files,
            tel_consts.TEL_FILES_FOLER: get_files_folder,
            tel_consts.TEL_UPDATE_FILE: update_file_ident,
            tel_consts.TEL_INSERT_FILE: tel_insert_file,
        }

    # возвращаем sql текст по идентификатору
    def get_sql_text(self, ident, **kwargs):
        for k in kwargs:
            # обрабатываем строковые параметры
            if type(kwargs[k]) == str:
                kwargs[k] = re.sub("'", "''", kwargs[k])

        if ident in self.proc_list.keys():
            return self.proc_list[ident](**kwargs)


# ищем пользователя
def start(**kwargs):
    s = "exec tel_CheckUser '{login}', {chat_id}".format(login=kwargs['login'], chat_id=kwargs['chat_id'])
    return s


# список пользователей
def get_users(**kwargs):
    s = "select Login, Chat_id from tel_StaffLink where Del = 0 and Chat_id is not NULL"
    return s


# список сотрудников
def get_staff(**kwargs):
    if ('ext' in kwargs.keys()) and (kwargs['ext'] != 0):
        text = '{"Notify":"' + str(kwargs['ext']) + '"}'
    else:
        text = kwargs['text']
    s = "exec tel_GetStaff '{login}', '{text}'".format(login=kwargs['login'], text=text)
    return s


# общая папка
def get_files_folder(**kwargs):
    s = "select id, s from _GlobalOptions where Name = 'PathToFiles'"
    return s


def tel_insert_file(**kwargs):
    s = "exec tel_InsertFile {_type}, {_id}, '{file_name}', '{login}', '{description}'".format(
        _id=kwargs['_id'],
        login=kwargs['login'],
        file_name=kwargs['file_name'],
        _type=kwargs['_type'],
        description=kwargs['description']
    )
    return s


# список файлов
def get_files(**kwargs):
    s = "tel_GetFiles {_type}, {_id}, '{login}'".format(
        _type=kwargs['_type'],
        _id=kwargs['_id'],
        login=kwargs['login'],
    )
    return s


# записываем идентификатор файла
def update_file_ident(**kwargs):
    s = "exec tel_UpdateFiles {id}, '{file_ident}', '{login}'".format(
        file_ident=kwargs['file_ident'],
        id=kwargs['_id'],
        login=kwargs['login']
    )
    return s


# новые задачи
def new_tasks(**kwargs):
    if 'text' in kwargs.keys():
        return "exec tel_GetDisposals '{login}', '{text}'".format(login=kwargs['login'], text=kwargs['text'])
    else:
        return "exec tel_GetDisposals '{login}'".format(login=kwargs['login'])


# задача
def get_task(**kwargs):
    return "exec tel_GetDisposal {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# прочитанность
def read_task(**kwargs):
    return "exec tel_SetDisposalReaded {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# новые счета
def new_accounts(**kwargs):
    text = ''
    if 'text' in kwargs.keys():
        text = kwargs['text']
    if ('ext' in kwargs.keys()) and (kwargs['ext'] != 0):
        text = '{"Notify":"' + str(kwargs['ext']) + '"}'
    return "exec tel_GetAccounts '{login}', '{text}'".format(login=kwargs['login'], text=text)


# счёт
def get_account(**kwargs):
    return "exec tel_GetAccount {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование счёта
def agree_account(**kwargs):
    return "exec tel_SetAccountVisa {_id}, '{login}', 11".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование счёта
def disagree_account(**kwargs):
    return "exec tel_SetAccountVisa {_id}, '{login}', 12".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование счёта
def ignore_account(**kwargs):
    return "exec tel_SetAccountVisa {_id}, '{login}', 82".format(_id=kwargs['_id'], login=kwargs['login'])


# Перерписка
def note(**kwargs):
    return "exec tel_AddNote {_id}, '{login}', {_type}, '{text}'".format(
        _id=kwargs['_id'],
        login=kwargs['login'],
        text=kwargs['text'],
        _type=kwargs['_type'],
    )


# Уведомления
def get_notifications(**kwargs):
    return "exec tel_GetNotifications '{login}', '{date}'".format(
        login=kwargs['login'],
        date=kwargs['date'].strftime("%Y%m%d %H:%M:%S"))


# Визы
def get_visa(**kwargs):
    return "exec tel_GetVisa {_type}, '{_id}'".format(_id=kwargs['_id'], _type=kwargs['_type'])


# несогласованные документы
def new_coordinations(**kwargs):
    text = ''
    if 'text' in kwargs.keys():
        text = kwargs['text']
    if ('ext' in kwargs.keys()) and (kwargs['ext'] != 0):
        text = '{"Notify":"' + str(kwargs['ext']) + '"}'
    return "exec tel_GetDocCoordinations '{login}', '{text}'".format(login=kwargs['login'], text=text)


# документ
def get_coordination(**kwargs):
    return "exec tel_GetDocCoordination {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование документа
def agree_coordination(**kwargs):
    return "exec tel_SetCoordinationVisa {_id}, '{login}', 293".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование документа
def disagree_coordination(**kwargs):
    return "exec tel_SetCoordinationVisa {_id}, '{login}', 294".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование документа
def back_coordination(**kwargs):
    return "exec tel_SetCoordinationVisa {_id}, '{login}', 295".format(_id=kwargs['_id'], login=kwargs['login'])


# поиск регламентов
def get_documents(**kwargs):
    return "exec tel_GetDocuments '{login}', '{text}'".format(login=kwargs['login'], text=kwargs['text'])


# регламент
def get_document(**kwargs):
    return "exec tel_GetDocument {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# поиск клиентов
def get_clients(**kwargs):
    text = ''
    if 'text' in kwargs.keys():
        text = kwargs['text']
    if ('ext' in kwargs.keys()) and (kwargs['ext'] != 0):
        text = '{"Notify":"' + str(kwargs['ext']) + '"}'
    return "exec tel_GetClients '{login}', '{text}'".format(login=kwargs['login'], text=text)


# клиент
def get_client(**kwargs):
    return "exec tel_GetClient {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])
