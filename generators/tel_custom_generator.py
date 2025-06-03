from generators.tel_answers_generator import AnswersGenerator


# базовый класс для кастомных генераторов ответов
# добавляются объекты при инициализации базового класса
# содержат описания - процедур-обработчиков идентификаторов
class CustomGenerator:
    def __init__(self, base_generator: AnswersGenerator):
        self.base_generator = base_generator

    # вызов объекта по id для отображения
    async def try_call_by_id(self, ident, **kwargs):
        return None
