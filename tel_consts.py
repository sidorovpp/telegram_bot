TEL_CONFIG = 'config.json'
TEL_START = 'start'
TEL_HELP = 'help'

TEL_ACCOUNT_ID = 2252
TEL_TASK_ID = 1127
TEL_TASK_REG_ID = 1138
TEL_COORDINATION_ID = 53161
TEL_COORDINATION_REG_ID = 53169
TEL_DOCUMENT_ID = 52701
TEL_DOCUMENT_REG_ID = 52708
TEL_STAFF_ID = 735
TEL_STAFF_REG_ID = 771
TEL_ACCOUNT_REG_ID = 1979
TEL_CLIENT_ID = 51055
TEL_CONTR_CLIENT_ID = 911
TEL_CLIENT_REG_ID = 51063
TEL_PETITION_ID = 50390
TEL_SHOW_SHEET_ID = 53152
TEL_SHOW_SHEET_REG_ID = 53157

TEL_NEW_TASKS = 'new_t'
TEL_TASKS_UNREADED = 'task_t'
TEL_TASKS_TO_ME = 'task_f'
TEL_TASKS_FROM_ME = 'task_u'
TEL_READ_TASK = 'read_t'
TEL_TASK = 'task'
TEL_ADD_TASK = 'add_task'
TEL_TASK_STATES = {1: '❌', 2: '👍', 3: '✅', 4: '⏱', 5: '🛠'}
TEL_FIND_WORK_GROUP = 'task_wg'
TEL_GET_LINKED_DISPOSALS = 'task_ld'

TEL_NEW_ACCOUNTS = 'new_acc'
TEL_ACCOUNT = 'acc'
TEL_AGREE_ACCOUNT = 'agree_acc'
TEL_DISAGREE_ACCOUNT = 'dis_acc'
TEL_IGNORE_ACCOUNT = 'ignore_acc'
TEL_ACCOUNT_STATES = {0: '⌛', 11: '✅', 12: '❌', 82: '⬆'}

TEL_COORDINATION = 'coord'
TEL_NEW_COORDINATIONS = 'new_c'
TEL_AGREE_COORDINATION = 'agree_c'
TEL_DISAGREE_COORDINATION = 'dis_c'
TEL_BACK_COORDINATION = 'back_c'
TEL_COORD_STATES = {0: '⌛', 1: '✅', 2: '❌', -1: '👀'}

TEL_PETITIONS = 'pets'
TEL_PETITION = 'pet'
TEL_PETITION_STATES = {1: '📖', 2: '❔', 3: '🔄', 4: '🚹', 5: '📝', 6: '☑',
                       7: '⛔', 8: '🔙', 9: '❌', 10: '❌', 11: '❌', 12: '🚫'}
TEL_PETITION_GRAPH = 'pet_g'
TEL_PETITION_CLIENTS = 'pet_c'
TEL_PETITIONS_DSRIM = 'pet_d'
TEL_PETITIONS_BACK = 'pet_b'
TEL_PETITIONS_DISAGREE = 'pet_dis'
TEL_PETITIONS_MY = 'pet_my'
TEL_PETITIONS_DIR = 'pet_dir'

TEL_DOCUMENTS = 'docs'
TEL_DOCUMENT = 'doc'

TEL_CLIENTS = 'clients'
TEL_CLIENT = 'client'
TEL_CONTR_CLIENTS = 'c_clients'
TEL_CONTR_CLIENT = 'c_client'
TEL_CLIENT_SCORING = 'client_sc'
TEL_CONTR_INN = 'set_inn'
TEL_INN = 'inn'
TEL_CLIENT_DATA = 'client_d'
TEL_INN_REQUEST = 'inn_req'

TEL_SHOW_SHEET = 'sh'
TEL_SHOW_SHEETS = 'sh_'
TEL_SEND_SMS = 'sms'
TEL_CHECK_SMS = 'sms_check'
TEL_GET_SHOW_SHEET_CODE = 'g_ss_code'
TEL_CONFIRM_SHEET_CODE = 'c_ss_code'
TEL_GET_CLIENT_FROM_SHOW_SHEET = 'gc_ss'

TEL_NOTIFICATIONS = 'notify'
TEL_READ_NOTIFY = 'read_notify'
TEL_GET_MESSAGES = 'get_messages'
TEL_SET_MESSAGE_SENT = 'set_message_sent'
TEL_SAVE_CHAT = 'save_chat'

TEL_USERS = 'users'
TEL_VISA = 'visa'
TEL_NOTE = 'note'
TEL_READED = 'read'

TEL_STAFF = 'staff'
TEL_FIND_STAFF = 'find_staff'

TEL_FILES = 'files'
TEL_UPDATE_FILE = 'upd_file'
TEL_FILES_FOLDER = 'f_folder'
TEL_INSERT_FILE = 'f_insert'

TEL_MENU = 'menu'
TEL_VISA_MENU = 'visa_menu'
TEL_SET_VISA = 'set_visa'

TEL_SPECIFICATION = 'spec'

TEL_CANCEL = 'отмена'
TEL_MAIN_MENU = 'Меню'

TEL_INSERT_SMS_LOG = 'sms_log'
TEL_CHECK_SMS_DISABLE = 'check_sms_form'
TEL_INSERT_SMS_LOG_MAIN = 'sms_log_main'

TEL_SCORING_URL = 'http://192.168.0.9:8083/api/import/updateDvizhClientScoring'
TEL_SCORING_TOKEN = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ7XCJzdWJcIjogXCJEVklaSHZrYm5BUEkyXCJ9IiwiaWF0Ijo'
                     'xNzI2ODE0NDYxLCJuYmYiOjE3MjY4MTQ0NjEsImp0aSI6Ijg2MzY3MmVhLWVjM2UtNDcwOS1hNmJjLTY2Y2MxMTY2ZWU3YyI'
                     'sImV4cCI6MjU5MDgxNDQ2MSwidHlwZSI6ImFjY2VzcyIsImZyZXNoIjpmYWxzZX0.tJCrlwU7j8PLWggmwrardaYfcJan2fj'
                     'ac5d9PefMM1w')

# соответствие команды и действия
command_list = {
    'задача': TEL_NEW_TASKS,
    'счёт': TEL_NEW_ACCOUNTS,
    'счет': TEL_NEW_ACCOUNTS,
    'документ': TEL_NEW_COORDINATIONS,
    'сотрудник': TEL_STAFF,
    'регламент': TEL_DOCUMENTS,
    'клиент': TEL_CLIENTS,
    'документы': TEL_NEW_COORDINATIONS,
    'задачи': TEL_NEW_TASKS,
    'счета': TEL_NEW_ACCOUNTS,
    'заявки': TEL_PETITIONS,
    'задачи непрочитанные': TEL_TASKS_UNREADED,
    'задачи на меня': TEL_TASKS_TO_ME,
    'задачи от меня': TEL_TASKS_FROM_ME,
    'заявки дсрим': TEL_PETITIONS_DSRIM,
    'заявки бэк': TEL_PETITIONS_BACK,
    'заявки отклонено': TEL_PETITIONS_DISAGREE,
    'мои заявки': TEL_PETITIONS_MY,
    'заявки руководителю': TEL_PETITIONS_DIR,
    'код': TEL_SPECIFICATION,
    'показы': TEL_SHOW_SHEETS,
}

# соответствие идентификатора и действий (множественное и одиночное)
map_ids = {
    TEL_ACCOUNT_ID: [TEL_NEW_ACCOUNTS, TEL_ACCOUNT],
    TEL_COORDINATION_ID: [TEL_NEW_COORDINATIONS, TEL_COORDINATION],
    TEL_STAFF_ID: [TEL_STAFF, TEL_STAFF],
    TEL_STAFF_REG_ID: [TEL_STAFF, TEL_STAFF],
    TEL_ACCOUNT_REG_ID: [TEL_NEW_ACCOUNTS, TEL_ACCOUNT],
    TEL_CLIENT_ID: [TEL_CLIENTS, TEL_CLIENT],
    TEL_CONTR_CLIENT_ID: [TEL_CONTR_CLIENTS, TEL_CONTR_CLIENT],
    TEL_CLIENT_REG_ID: [TEL_CLIENTS, TEL_CLIENT],
    TEL_COORDINATION_REG_ID: [TEL_NEW_COORDINATIONS, TEL_COORDINATION],
    TEL_TASK_REG_ID: [TEL_NEW_TASKS, TEL_TASK],
    TEL_SHOW_SHEET_REG_ID: [TEL_SHOW_SHEETS, TEL_SHOW_SHEET],
    TEL_DOCUMENT_ID: [TEL_DOCUMENTS, TEL_DOCUMENT],
    TEL_DOCUMENT_REG_ID: [TEL_DOCUMENTS, TEL_DOCUMENT],
}

# соответствие идентификатора и действия
map_actions = {
    TEL_NEW_TASKS: [TEL_TASK, 'задач'],
    TEL_GET_LINKED_DISPOSALS: [TEL_TASK, 'задач'],
    TEL_NEW_ACCOUNTS: [TEL_ACCOUNT, 'счетов'],
    TEL_NEW_COORDINATIONS: [TEL_COORDINATION, 'документов'],
    TEL_PETITIONS: [TEL_PETITION, 'заявок'],
    TEL_DOCUMENTS: [TEL_DOCUMENT, 'регламентов'],
    TEL_CLIENTS: [TEL_CLIENT, 'клиентов'],
    TEL_CONTR_CLIENTS: [TEL_CONTR_CLIENT, 'контрагентов'],
    TEL_SHOW_SHEETS: [TEL_SHOW_SHEET, 'показов'],
}

img_lib = {
    'agree': '✅',
    'disagree': '❌',
    'see': '👀',
    'sign': '🖋',
    'exclamation': '❗',
    'smile': '😀',
    'arrow_down': '⬇',
    'arrow_up': '⬆',
    'man': '🚹',
    'building': '🏢',
    'money': '💸',
    'handshake': '🤝',
    'document': '📝',
    'number': '#️⃣',
    'confirm': '👍',
    'clock': '⏱',
    'hourglass': '⌛',
    'work': '🛠',
    'back': '🔙',
    'book': '📖',
    'question': '❔',
    'refresh': '🔄',
    'stop': '⛔',
    'prohibited': '🚫',
    'phone': '📞'
}

show_sheet_sms = ('Вы можете оценить работу менеджера показа по ссылке: '
                  'https://vkbn.shop/rating?manager_id={staff_id}&type_id=2&ext_id={show_sheet_id}')

main_menu = [[[TEL_MAIN_MENU,
               [
                   [
                       ['Документы', []],
                       ['Задачи',
                        [
                            [
                                ['Задачи на меня', []],
                                ['Задачи от меня', []],
                                ['Новая задача', []],
                            ],
                            [
                                ['Задачи непрочитанные', []],
                                [TEL_MAIN_MENU, []]
                            ]
                        ]
                        ]
                   ],
                   [
                       ['Счета', []],
                       ['Заявки',
                        [
                            [
                                ['Заявки ДСРиМ', []],
                                ['Заявки БЭК', []],
                                ['Заявки отклонено', []],
                            ],
                            [
                                ['Мои заявки', []],
                                ['Заявки руководителю', []],
                                [TEL_MAIN_MENU, []]
                            ]
                        ]
                        ],
                       ['Показы', []],
                   ]
               ]
               ]]]
