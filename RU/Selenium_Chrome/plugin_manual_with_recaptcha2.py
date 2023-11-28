# Импорт необходимых модулей
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import json

API_KEY = 'YOUR-ANTI-CAPTCHA-API-KEY'
DRIVER_PATH = './path/to/chromedriver'
PLUGIN_PATH = './plugin/path.zip'

# Метод для отправки API запросов напрямую в плагин
# Например, для инициализации API ключа сервиса anti-captcha.com, необходимого для работы плагина
# Работает только на активной HTML странице,
# в нашем случае на https://antcpt.com/blank.html
# запросы не пройдут на страницах типа about:blank


def acp_api_send_request(driver, message_type, data={}):
    message = {
        # всегда указывает на конкретного получателя API сообщения
        'receiver': 'antiCaptchaPlugin',
        # тип запроса, например, setOptions
        'type': message_type,
        # слияние с дополнительными данными
        **data
    }
    # выполнение JS кода на странице
    # а именно, отправка сообщения с помощью стандартного метода window.postMessage
    return driver.execute_script("""
    return window.postMessage({});
    """.format(json.dumps(message)))


def set_anti_captcha_api_key(browser, api_key: str):
    # Переходим на пустую страницу для выполнения API запроса к плагину
    browser.get('https://antcpt.com/blank.html')

    # Установка API ключа anti-captcha.com
    # замените YOUR-ANTI-CAPTCHA-API-KEY на ваш шестнадцатеричный ключ, который можно взять здесь:
    # https://anti-captcha.com/clients/settings/apisetup
    acp_api_send_request(
        browser,
        'setOptions',
        {'options': {'antiCaptchaApiKey': api_key}}
    )

    # Пауза в три секунды, чтобы плагин мог проверить API KEY на стороне anti-captcha.com
    time.sleep(3)


def get_browser_with_plugin_ready(plugin_path: str, driver_path: str, api_key: str):
    # Инициализация объекта Chrome options для подключения расширения
    options = webdriver.ChromeOptions()
    # Ссылка на файл CRX или ZIP плагина, который мы ранее скачали
    options.add_extension(plugin_path)

    # Создание объекта Browser (Chrome Web Driver), передав путь, куда был загружен файл драйвера
    browser = webdriver.Chrome(
        service=Service(driver_path),
        options=options
    )

    set_anti_captcha_api_key(
        browser=browser,
        api_key=api_key
    )

    return browser


browser = get_browser_with_plugin_ready(
    plugin_path=PLUGIN_PATH,
    # обратите внимание: на Windows он должен заканчиваться на ".exe"!
    driver_path=DRIVER_PATH,
    api_key=API_KEY
)

browser.get('https://anti-captcha.com/demo/?page=recaptcha_v2_textarea')

# ждем пока форма загрузится и появится поле ввода логина
WebDriverWait(browser, 5).until(EC.visibility_of_element_located((
    By.CSS_SELECTOR,
    'input[name=login]'
)))

# заполняем форму
login_input = browser.find_element(By.CSS_SELECTOR, 'input[name=login]')
login_input.send_keys('Test login')

password_input = browser.find_element(By.CSS_SELECTOR, 'input[name=pass]')
password_input.send_keys('Test password')

# ждем автоматического решения капчи плагином и появления элемента .antigate_solver.solved на странице
WebDriverWait(browser, 120).until(EC.visibility_of_element_located((
    By.CSS_SELECTOR,
    '.antigate_solver.solved'
)))

# отправляем форму
browser.find_element(By.CSS_SELECTOR, 'button').click()

# чтобы браузер не закрывался сразу и вы могли увидеть результат
input()
