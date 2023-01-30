# класс хранит элементы меню
import tel_consts as tc
import json


# фомрируем кнопки для клавиатуры телеграм
def make_buttons_menu(items):
    res = []
    for row in items:
        new_row = []
        for item in row:
            new_row.append(item[0])
        res.append(new_row)
    return res


# ищем нужный уровень по названию материнской кнопки
def get_main_menu(caption):
    def find_item(items, _caption):
        # первый уровень - ряды
        for row in items:
            # второй уровень - кнопки
            for item in row:
                if item[0] == _caption:
                    return item[1]
                if item[1]:
                    res = find_item(item[1], _caption)
                    if res:
                        return res

    return find_item(tc.main_menu, caption)


class Menu:
    def __init__(self):
        self.menu_list = []

    # поиск по главному меню

    # поиск меню по идентифкатору и пользователю
    def get_menu(self, ident, login, ext_items):
        for menu in self.menu_list:
            if menu['login'] == login and menu['ident'] == ident:
                menu['ext_items'] = ext_items
                return menu['index']

    # поиск меню по индексу
    def get_menu_by_index(self, index):
        for menu in self.menu_list:
            if menu['index'] == index:
                return menu

    # перебираем меню с дочерними
    def get_items(self, items):
        for item in items:
            yield item
            if len(item['child']) > 0:
                yield from self.get_items(item['child'])

    # возвращаем кнопки по меню и нажатой кнопке
    def get_keyboard_items(self, menu_index, item_id, _id):
        res = []
        menu = self.get_menu_by_index(menu_index)
        for item in self.get_items(menu['items']):
            if item['parent_id'] == item_id:
                if item['json'] == '':
                    res.append(
                        [[item['name'], {"ident": tc.TEL_MENU, "_id": _id, "ext": item['_id'], "_type": menu_index}]])
                else:
                    j = json.loads(item['json'])
                    j['_id'] = _id
                    res.append([[item['name'], j]])
        # добавляем дополнительные пункты
        if 'ext_items' in menu.keys():
            for item in menu['ext_items']:
                res.append(([[item['name'], json.loads(item['_json'])]]))
        return res

    # добавление меню для пользователя на основании датасета
    # ext_items -дополнительные кнопки в меню при вызове
    def add_menu(self, ident, frame, login, ext_items):

        def add_item(items: list, _id: int, parent_id: int, name: str, _json: str):
            new_item = {'_id': _id, 'parent_id': parent_id,
                        'name': name.format_map(tc.img_lib), 'json': _json, 'child': [], 'index': len(items) + 1}
            if new_item['parent_id'] == -1:
                items.append(new_item)
                return

            for item in self.get_items(items):
                if item['_id'] == new_item['parent_id']:
                    item['child'].append(new_item)
                    return

        menu = {'ident': ident, 'login': login, 'index': len(self.menu_list) + 1}

        # перебираем датасет и добавляем элементы
        menu_items = []
        for i, row in frame.iterrows():
            add_item(menu_items, row['_id'], row['Parent_id'], row['Name'], row['_json'])

        menu['items'] = menu_items
        if ext_items:
            menu['ext_items'] = ext_items

        self.menu_list.append(menu)

        return menu['index']
