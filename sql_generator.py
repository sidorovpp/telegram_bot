import tel_consts as tc
import re


class SQLGenerator:
    def __init__(self):
        self.proc_list = {
            tc.TEL_USERS: get_users,
            tc.TEL_START: start,

            tc.TEL_VISA: get_visa,
            tc.TEL_NOTE: get_note,

            tc.TEL_NEW_TASKS: get_new_tasks,
            tc.TEL_TASK: get_task,
            tc.TEL_READ_TASK: get_read_task,
            tc.TEL_READED: get_readed,
            tc.TEL_ADD_TASK: get_add_task,
            tc.TEL_FIND_WORK_GROUP: get_find_work_group,
            tc.TEL_GET_LINKED_DISPOSALS: get_linked_disposals,

            tc.TEL_NEW_ACCOUNTS: get_new_accounts,
            tc.TEL_ACCOUNT: get_account,
            tc.TEL_AGREE_ACCOUNT: get_agree_account,
            tc.TEL_DISAGREE_ACCOUNT: get_disagree_account,
            tc.TEL_IGNORE_ACCOUNT: get_ignore_account,

            tc.TEL_NEW_COORDINATIONS: get_new_coordinations,
            tc.TEL_COORDINATION: get_coordination,
            tc.TEL_AGREE_COORDINATION: get_agree_coordination,
            tc.TEL_DISAGREE_COORDINATION: get_disagree_coordination,
            tc.TEL_BACK_COORDINATION: get_back_coordination,

            tc.TEL_PETITIONS: get_petitions,
            tc.TEL_PETITION: get_petition,
            tc.TEL_PETITION_GRAPH: get_petition_graph,
            tc.TEL_PETITION_CLIENTS: get_petition_clients,

            tc.TEL_DOCUMENTS: get_documents,
            tc.TEL_DOCUMENT: get_document,

            tc.TEL_CLIENTS: get_clients,
            tc.TEL_CLIENT: get_client,
            tc.TEL_CONTR_CLIENTS: get_contr_clients,
            tc.TEL_CONTR_CLIENT: get_contr_client,
            tc.TEL_CONTR_INN: get_set_client_inn,
            tc.TEL_CLIENT_SCORING: get_client_scoring,
            tc.TEL_CLIENT_DATA: get_client_data,

            tc.TEL_STAFF: get_staff,
            tc.TEL_FIND_STAFF: get_find_staff,

            tc.TEL_NOTIFICATIONS: get_notifications,
            tc.TEL_READ_NOTIFY: get_read_notify,
            tc.TEL_GET_MESSAGES: get_messages,
            tc.TEL_SET_MESSAGE_SENT: set_message_sent,
            tc.TEL_SAVE_CHAT: save_chat,

            tc.TEL_FILES: get_files,
            tc.TEL_FILES_FOLDER: get_files_folder,
            tc.TEL_UPDATE_FILE: update_file_ident,
            tc.TEL_INSERT_FILE: tel_insert_file,

            tc.TEL_VISA_MENU: get_visa_menu,
            tc.TEL_SET_VISA: get_set_visa,

            tc.TEL_SHOW_SHEETS: get_show_sheets,
            tc.TEL_SHOW_SHEET: get_show_sheet,
            tc.TEL_GET_SHOW_SHEET_CODE: get_show_sheet_code,
            tc.TEL_CONFIRM_SHEET_CODE: confirm_show_sheet_code,
            tc.TEL_GET_CLIENT_FROM_SHOW_SHEET: get_client_from_show_sheet,

            tc.TEL_SPECIFICATION: get_specification,

            tc.TEL_INSERT_SMS_LOG: tel_insert_sms_log,
            tc.TEL_CHECK_SMS_DISABLE: tel_check_sms_disable,
            tc.TEL_INSERT_SMS_LOG_MAIN: tel_insert_sms_log_main,
        }

    # возвращаем sql текст по идентификатору
    def get_sql_text(self, ident, **kwargs):
        for k in kwargs:
            # обрабатываем строковые параметры
            if type(kwargs[k]) == str:
                kwargs[k] = re.sub("'", "''", kwargs[k])

        if ident in self.proc_list.keys():
            return self.proc_list[ident](**kwargs)


# возвращаем текст для поиска из параметров
def get_text_from_params(**kwargs):
    text = ''
    if 'text' in kwargs.keys():
        text = kwargs['text']
    if ('ext' in kwargs.keys()) and (kwargs['ext'] != 0):
        text = '{"Notify":"' + str(kwargs['ext']) + '"}'
    return text


# возвращаем mode, если есть, иначе 0 - стандартный режим
def get_mode_from_params(**kwargs):
    if 'mode' in kwargs.keys():
        res = kwargs['mode']
    else:
        res = 0
    return res


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
    text = get_text_from_params(**kwargs)
    s = "exec tel_GetStaff '{login}', '{text}'".format(login=kwargs['login'], text=text)
    return s


# общая папка
def get_files_folder(**kwargs):
    s = "select id, s from _GlobalOptions where Name = 'PathToFiles'"
    return s


def tel_insert_file(**kwargs):
    if not kwargs['description']:
        kwargs['description'] = ''
    s = "exec tel_InsertFile {_type}, {_id}, '{file_name}', '{login}', '{description}'".format(
        _id=kwargs['_id'],
        login=kwargs['login'],
        file_name=kwargs['file_name'],
        _type=kwargs['_type'],
        description=kwargs['description']
    )
    return s


# лог по пользователю - отправка СМС
def tel_insert_sms_log(**kwargs):
    s = "exec tel_InsertSMSLog '{login}', '{phone}', '{text}'".format(
        login=kwargs['login'],
        phone=kwargs['phone'],
        text=kwargs['text'],
    )
    return s


# проверка блокировки формы СМС
def tel_check_sms_disable(**kwargs):
    s = "exec srv_GetSMSForm '{ident}'".format(
        ident=kwargs['form'],
    )
    return s


# лог по отправке СМС общий
def tel_insert_sms_log_main(**kwargs):
    s = "exec srv_SaveSMSLog '{number}', '{text}', '{form}', {balance}, {price}, '{host}', {send_whatsapp}".format(
        number=kwargs['number'],
        text=kwargs['text'],
        form=kwargs['form'],
        balance=kwargs['balance'],
        price=kwargs['price'],
        host=kwargs['host'],
        send_whatsapp=kwargs['send_whatsapp']
    )
    return s


# список файлов
def get_files(**kwargs):
    s = "exec tel_GetFiles {_type}, {_id}, '{login}'".format(
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
def get_new_tasks(**kwargs):
    return "exec tel_GetDisposals '{login}', '{text}', {mode}".format(
        login=kwargs['login'],
        text=get_text_from_params(**kwargs),
        mode=get_mode_from_params(**kwargs))


# связанные задачи
def get_linked_disposals(**kwargs):
    return "exec tel_GetLinkedDisposals '{login}', '{_id}'".format(login=kwargs['login'], _id=kwargs['_id'])


# задача
def get_task(**kwargs):
    return "exec tel_GetDisposal {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# прочитанность
def get_read_task(**kwargs):
    return "exec tel_SetDisposalReaded {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# новые счета
def get_new_accounts(**kwargs):
    return "exec tel_GetAccounts '{login}', '{text}'".format(
        login=kwargs['login'],
        text=get_text_from_params(**kwargs))


# счёт
def get_account(**kwargs):
    return "exec tel_GetAccount {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование счёта
def get_agree_account(**kwargs):
    return "exec tel_SetAccountVisa {_id}, '{login}', 11".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование счёта
def get_disagree_account(**kwargs):
    return "exec tel_SetAccountVisa {_id}, '{login}', 12".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование счёта
def get_ignore_account(**kwargs):
    return "exec tel_SetAccountVisa {_id}, '{login}', 82".format(_id=kwargs['_id'], login=kwargs['login'])


# Перерписка
def get_note(**kwargs):
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


# Уведомления
def get_read_notify(**kwargs):
    return "exec tel_SetNotifyReaded '{_id}', '{login}'".format(
        _id=kwargs['_id'],
        login=kwargs['login'])


# Визы
def get_visa(**kwargs):
    return "exec tel_GetVisa {_type}, {_id}".format(_id=kwargs['_id'], _type=kwargs['_type'])


# прочитали
def get_readed(**kwargs):
    return "exec tel_GetReaded {_type}, {_id}".format(_id=kwargs['_id'], _type=kwargs['_type'])


# несогласованные документы
def get_new_coordinations(**kwargs):
    text = get_text_from_params(**kwargs)
    return "exec tel_GetDocCoordinations '{login}', '{text}'".format(login=kwargs['login'], text=text)


# документ
def get_coordination(**kwargs):
    return "exec tel_GetDocCoordination {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование документа
def get_agree_coordination(**kwargs):
    return "exec tel_SetCoordinationVisa {_id}, '{login}', 293".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование документа
def get_disagree_coordination(**kwargs):
    return "exec tel_SetCoordinationVisa {_id}, '{login}', 294".format(_id=kwargs['_id'], login=kwargs['login'])


# Согласование документа
def get_back_coordination(**kwargs):
    return "exec tel_SetCoordinationVisa {_id}, '{login}', 295".format(_id=kwargs['_id'], login=kwargs['login'])


# поиск регламентов
def get_documents(**kwargs):
    text = get_text_from_params(**kwargs)
    return "exec tel_GetDocuments '{login}', '{text}'".format(login=kwargs['login'], text=text)


# регламент
def get_document(**kwargs):
    return "exec tel_GetDocument {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# поиск клиентов
def get_clients(**kwargs):
    text = get_text_from_params(**kwargs)
    return "exec tel_GetClients '{login}', '{text}'".format(login=kwargs['login'], text=text)


# клиент
def get_client(**kwargs):
    return "exec tel_GetClient {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# поиск контрагентов
def get_contr_clients(**kwargs):
    text = get_text_from_params(**kwargs)
    return "exec tel_GetContrClients '{login}', '{text}'".format(login=kwargs['login'], text=text)


# контрагент
def get_contr_client(**kwargs):
    return "exec tel_GetContrClient {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# записываем ИНН в контрагента
def get_set_client_inn(**kwargs):
    return "update clients set INN = '{inn}' where id = {_id}".format(_id=kwargs['_id'], inn=kwargs['inn'])


# скоринг клиента и загрузка из базы
def get_client_scoring(**kwargs):
    return "exec tel_GetClientScoring {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# данные клиента для сайта налоговой
def get_client_data(**kwargs):
    return "exec tel_GetClientDataForINN {_id}".format(_id=kwargs['_id'])


# загрузка меню по визам
def get_visa_menu(**kwargs):
    return "exec tel_GetVisaMenu {_type}, '{login}'".format(_type=kwargs['_type'], login=kwargs['login'])


# устанавливаем визу
def get_set_visa(**kwargs):
    return "exec tel_SetVisa {_id}, '{login}', {_type}, {ext}".format(
        _type=kwargs['_type'],
        login=kwargs['login'],
        _id=kwargs['_id'],
        ext=kwargs['ext'])


# заявки на продажу квартир
def get_petitions(**kwargs):
    return "exec tel_GetPetitions '{login}', '{text}', {mode}".format(
        login=kwargs['login'],
        text=kwargs['text'],
        mode=get_mode_from_params(**kwargs))


# заявка на продажу квартир
def get_petition(**kwargs):
    return "exec tel_GetPetition {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# график платежей по заявке
def get_petition_graph(**kwargs):
    return "exec tel_GetPetitionGraph {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# клиенты по заявке
def get_petition_clients(**kwargs):
    return "exec tel_GetPetitionClients {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# поиск сотрудника
def get_find_staff(**kwargs):
    return "exec tel_FindStaff '{text}'".format(text=kwargs['text'])


# поиск рабочей группы
def get_find_work_group(**kwargs):
    return "exec tel_FindWorkGroup '{text}'".format(text=kwargs['text'])


# создание новой задачи
def get_add_task(**kwargs):
    return "exec tel_AddTask '{login}', '{theme}', '{task}', {receiver}, {urgency}, {work_group}".format(
        login=kwargs['login'],
        theme=kwargs['theme'],
        task=kwargs['task'],
        receiver=kwargs['receiver'],
        urgency=kwargs['urgency'],
        work_group=kwargs['work_group']
    )


# поиск спецификации
def get_specification(**kwargs):
    return "exec tel_GetSpecification '{text}', '{login}'".format(
        text=kwargs['text'],
        login=kwargs['login']
    )


# загрузка неотправленных сообщений спецификации
def get_messages(**kwargs):
    return "select id, chat_id, message from tel_Messages where DateComplete is NULL"


# загрузка неотправленных сообщений спецификации
def set_message_sent(**kwargs):
    return "update tel_Messages set DateComplete = getdate() where id = {id}".format(
        id=kwargs['id']
    )


def save_chat(**kwargs):
    return "exec tel_SaveGroupChat {chat_id}, '{description}'".format(
        chat_id=kwargs['chat_id'],
        description=kwargs['description'],
    )


# смотровые листы
def get_show_sheets(**kwargs):
    date = 'NULL'
    if 'date' in kwargs:
        date = "'" + kwargs['date'] + "'"
    return "exec tel_GetShowSheets '{login}', '{text}', {mode}, {date}".format(
        login=kwargs['login'],
        text=get_text_from_params(**kwargs),
        mode=get_mode_from_params(**kwargs),
        date=date
    )


# смотровой лист
def get_show_sheet(**kwargs):
    return "exec tel_GetShowSheet {_id}, '{login}'".format(_id=kwargs['_id'], login=kwargs['login'])


# запись и получение кода смотрового листа
def get_show_sheet_code(**kwargs):
    return "exec tel_GetShowSheetCode {_id}, {refresh}".format(_id=kwargs['_id'], refresh=kwargs['refresh'])


# запись подтверждения кода смотрового листа
def confirm_show_sheet_code(**kwargs):
    return "exec tel_ConfirmShowSheetCode {_id}".format(_id=kwargs['_id'])


# получаем клиента из смотрового листа
def get_client_from_show_sheet(**kwargs):
    return "select PotentialClient_id client_id from r_ShowSheets where id = {_id}".format(_id=kwargs['_id'])
