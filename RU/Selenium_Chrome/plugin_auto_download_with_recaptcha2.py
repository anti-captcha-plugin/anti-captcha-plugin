# Импорт необходимых модулей
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import os
import pathlib
import urllib.request
import zipfile

API_KEY = 'YOUR-ANTI-CAPTCHA-API-KEY'
DRIVER_PATH = './path/to/chromedriver'
PLUGIN_PATH = './plugin/path.zip'


def prepare_plugin(anti_captcha_api_key: str):
    current_script_dir = str(pathlib.Path(__file__).parent.resolve())
    modified_plugin_path = current_script_dir + '/plugin_hardcoded_api_key.zip'
    plugin_extract_path = current_script_dir + '/extracted_plugin'

    # скачиваем плагин
    url = 'https://antcpt.com/anticaptcha-plugin.zip'
    filehandle, _ = urllib.request.urlretrieve(url)

    # распаковываем его
    with zipfile.ZipFile(filehandle, "r") as f:
        f.extractall(path=plugin_extract_path)

    # устанавливаем API ключ в файл конфигурации
    file = pathlib.Path(plugin_extract_path + '/js/config_ac_api_key.js')
    file.write_text(file.read_text().replace(
        "antiCapthaPredefinedApiKey = ''",
        "antiCapthaPredefinedApiKey = '{}'".format(anti_captcha_api_key)
    ))

    # перепаковываем директорию плагина
    zip_file = zipfile.ZipFile(modified_plugin_path, 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(plugin_extract_path):
        for file in files:
            path = os.path.join(root, file)
            zip_file.write(
                path,
                arcname=path.replace(plugin_extract_path, ''))

    zip_file.close()

    return modified_plugin_path


def get_browser_with_plugin_ready(driver_path: str, api_key: str):
    # Инициализируем объект Chrome options, чтобы подключить расширение
    options = webdriver.ChromeOptions()

    # Чтобы Selenium мог сразу же вернуть управление нашему коду сразу после начала загрузки страницы
    # иначе, если какие-то ресурсы будут долго загружаться на странице, управление
    # не вернётся пока страница полностью не загрузится, это может продолжаться десятки секунд
    options.page_load_strategy = 'none'

    # плагин автоматически загружается и ваш ключ Anti-Captcha встраивается в него
    plugin_path = prepare_plugin(api_key)
    options.add_extension(plugin_path)

    # Создаём объект Browser (Chrome Web Driver), передав путь до файла, куда был загружен файл драйвера
    return webdriver.Chrome(
        service=Service(driver_path),
        options=options
    )


browser = get_browser_with_plugin_ready(
    # обратите внимание: на Windows он должен заканчиваться на ".exe"!
    driver_path=DRIVER_PATH,
    api_key=API_KEY
)

browser.get('https://anti-captcha.com/demo/?page=recaptcha_v2_textarea')

# ждём пока форма загрузится и появится поле ввода логина
WebDriverWait(browser, 5).until(EC.visibility_of_element_located((
    By.CSS_SELECTOR,
    'input[name=login]'
)))

# заполняем форму
login_input = browser.find_element(By.CSS_SELECTOR, 'input[name=login]')
login_input.send_keys('Test login')

password_input = browser.find_element(By.CSS_SELECTOR, 'input[name=pass]')
password_input.send_keys('Test password')

# ждём автоматического решения капчи плагином и появления элемента .antigate_solver.solved на странице
WebDriverWait(browser, 120).until(EC.visibility_of_element_located((
    By.CSS_SELECTOR,
    '.antigate_solver.solved'
)))

# отправляем форму
browser.find_element(By.CSS_SELECTOR, 'button').click()

# чтобы браузер сразу не закрылся, и вы могли увидеть результат
input()
