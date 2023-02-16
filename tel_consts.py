TEL_CONFIG = 'config.json'
TEL_START = 'start'
TEL_HELP = 'help'

TEL_ACCOUNT_ID = 2252
TEL_TASK_ID = 1127
TEL_TASK_REG_ID = 1138
TEL_COORDINATION_ID = 53161
TEL_COORDINATION_REG_ID = 53169
TEL_DOCUMENT_ID = 52701
TEL_STAFF_ID = 735
TEL_STAFF_REG_ID = 771
TEL_ACCOUNT_REG_ID = 1979
TEL_CLIENT_ID = 51055
TEL_CLIENT_REG_ID = 51063
TEL_PETITION_ID = 50390

TEL_NEW_TASKS = 'new_t'
TEL_TASKS_UNREADED = 'task_t'
TEL_TASKS_TO_ME = 'task_f'
TEL_TASKS_FROM_ME = 'task_u'
TEL_READ_TASK = 'read_t'
TEL_TASK = 'task'
TEL_ADD_TASK = 'add_task'
TEL_TASK_STATES = {1: '❌', 2: '👍', 3: '✅', 4: '⏱', 5: '🛠'}
TEL_FIND_WORK_GROUP = 'task_wg'

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

TEL_NOTIFICATIONS = 'notify'
TEL_READ_NOTIFY = 'read_notify'
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

# соответсвие команды и действия
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
}

# соовтетствие идентификатора и действий (множественное и одиночное)
map_ids = {
    TEL_ACCOUNT_ID: [TEL_NEW_ACCOUNTS, TEL_ACCOUNT],
    TEL_COORDINATION_ID: [TEL_NEW_COORDINATIONS, TEL_COORDINATION],
    TEL_STAFF_ID: [TEL_STAFF, TEL_STAFF],
    TEL_STAFF_REG_ID: [TEL_STAFF, TEL_STAFF],
    TEL_ACCOUNT_REG_ID: [TEL_NEW_ACCOUNTS, TEL_ACCOUNT],
    TEL_CLIENT_ID: [TEL_CLIENTS, TEL_CLIENT],
    TEL_CLIENT_REG_ID: [TEL_CLIENTS, TEL_CLIENT],
    TEL_COORDINATION_REG_ID: [TEL_NEW_COORDINATIONS, TEL_COORDINATION],
    TEL_TASK_REG_ID: [TEL_NEW_TASKS, TEL_TASK]
}

img_lib = {
    'agree': '✅',
    'disagree': '❌',
    'see': '👀',
    'sign': '🖋',
    'exclamation': '❗',
    'smile': '😀',
    'arrow_down': '⬇',
    'man': '🚹',
    'building': '🏢',
    'money': '💸',
    'handshake': '🤝',
    'document': '📝',
    'number': '#️⃣'
}

main_menu = [[['Главное меню',
               [
                   [
                       ['Документы', []],
                       ['Задачи',
                        [
                            [
                                ['Задачи на меня', []],
                                ['Задачи от меня', []]
                            ],
                            [
                                ['Задачи непрочитанные', []],
                                ['Главное меню', []]
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
                                ['Главное меню', []]
                            ]
                        ]
                        ]
                   ]
               ]
               ]]]
