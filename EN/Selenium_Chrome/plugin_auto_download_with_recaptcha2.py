# Import the necessary modules
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


def prepare_plugin(anti_captcha_api_key: str):
    current_script_dir = str(pathlib.Path(__file__).parent.resolve())
    modified_plugin_path = current_script_dir + '/plugin_hardcoded_api_key.zip'
    plugin_extract_path = current_script_dir + '/extracted_plugin'

    # download the plugin
    url = 'https://antcpt.com/anticaptcha-plugin.zip'
    filehandle, _ = urllib.request.urlretrieve(url)

    # unpack it
    with zipfile.ZipFile(filehandle, "r") as f:
        f.extractall(path=plugin_extract_path)

    # set the API key in the configuration file
    file = pathlib.Path(plugin_extract_path + '/js/config_ac_api_key.js')
    file.write_text(file.read_text().replace(
        "antiCapthaPredefinedApiKey = ''",
        "antiCapthaPredefinedApiKey = '{}'".format(anti_captcha_api_key)
    ))

    # repack the plugin directory
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
    # Initiate Chrome options object to be able to connect the extension
    options = webdriver.ChromeOptions()

    # To allow Selenium to return control to our code immediately after the page starts loading
    # otherwise, if some resources take a long time to load on the page, control
    # won't return for dozens of seconds until the page is fully loaded
    options.page_load_strategy = 'none'

    # the plugin is automatically downloaded and your Anti-Captcha key is embedded in it
    plugin_path = prepare_plugin(api_key)
    options.add_extension(plugin_path)

    # Create a Browser object (Chrome Web Driver) passing the path where the driver file was downloaded
    return webdriver.Chrome(
        service=Service(driver_path),
        options=options
    )


browser = get_browser_with_plugin_ready(
    driver_path=DRIVER_PATH,  # note: on Windows it should end with ".exe"!
    api_key=API_KEY
)

browser.get('https://anti-captcha.com/demo/?page=recaptcha_v2_textarea')

# wait until the form loads and the login input field appears
WebDriverWait(browser, 5).until(EC.visibility_of_element_located((
    By.CSS_SELECTOR,
    'input[name=login]'
)))

# fill out the form
login_input = browser.find_element(By.CSS_SELECTOR, 'input[name=login]')
login_input.send_keys('Test login')

password_input = browser.find_element(By.CSS_SELECTOR, 'input[name=pass]')
password_input.send_keys('Test password')

# wait for the captcha to be automatically solved by the plugin and the element .antigate_solver.solved appears on the page
WebDriverWait(browser, 120).until(EC.visibility_of_element_located((
    By.CSS_SELECTOR,
    '.antigate_solver.solved'
)))

# submit the form
browser.find_element(By.CSS_SELECTOR, 'button').click()

# to prevent the browser from closing immediately so you can see the result
input()
