from playwright.async_api import async_playwright, expect
import logging
import traceback


def only_digits(number: str) -> str:
    res = ''
    for i in number:
        if i.isdigit():
            res = res + i
    return res


# фирма
def calc_company_check_digit(number):
    weights = (2, 4, 10, 3, 5, 9, 4, 6, 8)
    return str(sum(w * int(n) for w, n in zip(weights, number)) % 11 % 10)


# человек
def calc_personal_check_digits(number):
    weights = (7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
    d1 = str(sum(w * int(n) for w, n in zip(weights, number)) % 11 % 10)
    weights = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
    d2 = str(sum(w * int(n) for w, n in zip(weights, number[:10] + d1)) % 11 % 10)
    return d1 + d2


# проверка ИНН
def validate(number: str) -> bool:
    number = only_digits(number)
    if len(number) == 10:
        if calc_company_check_digit(number) != number[-1]:
            return False
    elif len(number) == 12:
        if calc_personal_check_digits(number) != number[-2:]:
            return False
    else:
        return False
    return True


async def get_inn(frame):
    if not frame.empty:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                await page.goto('https://service.nalog.ru/static/personal-data.html?svc=inn&from=%2Finn.do')

                # страница подтверждения
                el = page.locator("#unichk_0")
                await el.click()
                el = page.locator("#btnContinue")
                await el.click()
                # вводим данные

                el = page.locator("#fam")
                await el.fill(frame['last_name'].values[0])
                el = page.locator("#nam")
                await el.fill(frame['first_name'].values[0])
                el = page.locator("#otch")
                await el.fill(frame['surname'].values[0])
                el = page.locator("#bdate")
                await el.fill(frame['birthday'].values[0])
                el = page.locator("#docno")
                await el.fill(frame['passport'].values[0])
                el = page.locator("#docdt")
                await el.fill(frame['passport_obtained_at'].values[0])
                el = page.locator("#btn_send")
                await el.click()

                # получаем ИНН
                el = page.locator("#resultInn")
                await expect(el).to_be_visible(timeout=120000)
                inn = await el.inner_text()

                await browser.close()

                res = inn
        except (Exception,):
            logging.error(traceback.format_exc())
            res = 'Ошибка получения ИНН'
    else:
        res = 'Клиент не найден!'
    return res
