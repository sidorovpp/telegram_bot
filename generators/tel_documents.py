import tel_consts as tc
from generators.tel_custom_generator import CustomGenerator
from generators.tel_answers_generator import get_doc_with_notes, AnswersGenerator, get_json_params
from telegram import InlineKeyboardButton


class DocumentsGenerator(CustomGenerator):
    def __init__(self, base_generator: AnswersGenerator):
        super().__init__(base_generator)
        self.base_generator.proc_list.update(
            {tc.TEL_DOCUMENT: self.get_document})

    # регламентный документ
    async def get_document(self, ident, **kwargs):
        frame = await self.base_generator.get_data_frame(ident, _id=kwargs['_id'], login=kwargs['login'])
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
