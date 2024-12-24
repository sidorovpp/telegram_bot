from smb.SMBConnection import SMBConnection
import tel_consts as tc
import json
import tempfile
import cv2
from pyzbar.pyzbar import decode
from os.path import splitext
import aiohttp
import logging
import traceback

allow_share = [
    '\\\\192.168.0.8\\Images', '\\\\192.168.0.8\\Документы', '\\\\192.168.0.8\\Общедоступные документы',
    '\\\\vkbdisk\\Images', '\\\\vkbdisk\\Документы', '\\\\vkbdisk\\Общедоступные документы'
]
with open(tc.TEL_CONFIG, 'r') as f:
    config = json.load(f)
    user_id = config['file_login']
    password = config['file_password']
    domain_name = 'vkbdisk'


# получаем значение из QR
def read_qr_code(file_name):
    try:
        image = cv2.imread(file_name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        values = decode(image)
        if values:
            return values[0].data
        else:
            return ''
    except (Exception,):
        return ''


# получаем файл по SMB из хранилища vkbdisk
def get_shared_file(file_name: str):
    check = False
    for share in allow_share:
        if file_name.lower().find(share.lower()) != -1:
            check = True
            break
    if not check:
        return None

    # подменяем на ip и приводим в нормальный вид
    file_name = file_name.replace('vkbdisk', '192.168.0.8')
    file_name = file_name.replace('\\', '/')
    splits = file_name.replace('//', '').split('/')
    server_ip = splits[0]
    service_name = splits[1]
    last_path = '/'.join(splits[2:])
    # отделяем расширение
    suffix = splits[len(splits) - 1]
    suffix = suffix[suffix.find('.'):]

    # загружаем файл в память
    conn = SMBConnection(
        username=user_id,
        password=password,
        my_name='',
        remote_name='',
        domain=domain_name,
        use_ntlm_v2=True,
        is_direct_tcp=True)
    conn.connect(server_ip, 445)
    _f = tempfile.NamedTemporaryFile(suffix=suffix)
    conn.retrieveFile(service_name=service_name, path=last_path, file_obj=_f)
    return _f


async def send_error(context, text):
    try:
        # посылаю себе текст с ошибкой
        await context.bot.send_message(1535958791, text)
    except (Exception,):
        logging.error(traceback.format_exc())
    pass


def create_shared_file(file_dir: str, file_name: str, file_object):
    # подменяем на ip и приводим в нормальный вид
    file_dir = file_dir.replace('vkbdisk', '192.168.0.8')
    file_dir = file_dir.replace('\\', '/')
    splits = file_dir.replace('//', '').split('/')
    server_ip = splits[0]
    service_name = splits[1]
    last_path = '/'.join(splits[2:])

    # загружаем файл в память
    conn = SMBConnection(
        username=user_id,
        password=password,
        my_name='',
        remote_name='',
        domain=domain_name,
        use_ntlm_v2=True,
        is_direct_tcp=True)
    conn.connect(server_ip, 445)
    # создаём папку
    try:
        conn.createDirectory(service_name=service_name, path=last_path)
    except (Exception,):
        pass  # если уже существует, идём дальше

    # ищем файл в папке, если есть - дополняем название
    i = 0
    search_file = file_name
    split = splitext(file_name)
    while conn.listPath(service_name=service_name, path=last_path, pattern=search_file):
        search_file = split[0] + str(i) + split[1]
        i = i + 1
    file_name = search_file

    # записываем файл
    conn.storeFile(service_name=service_name, path=last_path + '\\' + file_name, file_obj=file_object)
    return file_name


# отправка СМС через сервис отправки
async def send_sms_to_service(message: str, number: str, form: str):
    token = config['sms_token']
    sms_host = config['sms_host']
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    data = {
        'text': message,
        'recipients': number,
        'form': form
    }
    async with aiohttp.ClientSession() as session:
        await session.post('http://' + sms_host + '/api/system/sendSMS/', headers=headers, data=json.dumps(data))
