TEL_CONFIG = 'config.json'
TEL_START = 'start'
TEL_HELP = 'help'

TEL_ACCOUNT_ID = 2252
TEL_TASK_ID = 1127
TEL_COORDINATION_ID = 53161
TEL_COORDINATION_REG_ID = 53169
TEL_DOCUMENT_ID = 52701
TEL_STAFF_ID = 735
TEL_STAFF_REG_ID = 771
TEL_ACCOUNT_REG_ID = 1979
TEL_CLIENT_ID = 51055
TEL_CLIENT_REG_ID = 51063

TEL_NEW_TASKS = 'new_t'
TEL_READ_TASK = 'read_t'
TEL_TASK = 'task'
TEL_TASK_STATES = {1: '❌', 2: '👍', 3: '✅', 4: '⏱', 5: '🛠'}

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

TEL_DOCUMENTS = 'docs'
TEL_DOCUMENT = 'doc'

TEL_CLIENTS = 'clients'
TEL_CLIENT = 'client'

TEL_NOTIFICATIONS = 'notify'
TEL_USERS = 'users'
TEL_VISA = 'visa'
TEL_NOTE = 'note'
TEL_READED = 'read'

TEL_STAFF = 'staff'

TEL_FILES = 'files'
TEL_UPDATE_FILE = 'upd_file'
TEL_FILES_FOLER = 'f_folder'
TEL_INSERT_FILE = 'f_insert'

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
    'счета': TEL_NEW_ACCOUNTS
}
