import tel_consts as tc
from generators.tel_custom_generator import CustomGenerator
from generators.tel_answers_generator import AnswersGenerator, replace_symbols


class CommonGenerator(CustomGenerator):
    def __init__(self, base_generator: AnswersGenerator):
        super().__init__(base_generator)
        self.base_generator.proc_list.update(
            {
                tc.TEL_VISA: self.get_visa,
                tc.TEL_NOTE: self.get_note,
                tc.TEL_READED: self.get_readed,
                tc.TEL_FILES: self.get_files,
                tc.TEL_SET_VISA: self.get_set_visa,
            })

    # список установленных виз
    async def get_visa(self, ident, _id, **kwargs):
        frame = await self.base_generator.get_data_frame(ident, _id=_id, **kwargs)
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
        frame = await self.base_generator.get_data_frame(ident, _id=_id, **kwargs)
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

    # устанавливаем визу
    async def get_set_visa(self, ident, **kwargs):
        await self.base_generator.exec_empty(ident, _id=kwargs['_id'], login=kwargs['login'], _type=kwargs['_type'], ext=kwargs['ext'])
        if kwargs['ext'] == -1:
            return 'Подписано', [], []
        else:
            return 'Виза установлена', [], []

    # пишем переписку
    async def get_note(self, ident, **kwargs):
        # помечаем прочитанной
        await self.base_generator.exec_empty(ident, **kwargs)

        # перебираем кастомные генераторы
        for generator in self.base_generator.generators:
            res = await generator.try_call_by_id(kwargs['_type'], **kwargs)
            if res:
                return res

    # получаем список файлов
    async def get_files(self, ident, **kwargs):
        files = []
        frame = await self.base_generator.get_frame(ident, **kwargs)
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

