# Import the necessary modules
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

# Method for sending API requests directly to the plugin
# For example, to initialize the API key of the anti-captcha.com service, necessary for the plugin to work
# Works only on an active HTML page,
# in our case on https://antcpt.com/blank.html
# requests will not pass on pages like about:blank


def acp_api_send_request(driver, message_type, data={}):
    message = {
        # always indicates this specific recipient of the API message
        'receiver': 'antiCaptchaPlugin',
        # request type, for example, setOptions
        'type': message_type,
        # merge with additional data
        **data
    }
    # execute JS code on the page
    # namely, send the message using the standard method window.postMessage
    return driver.execute_script("""
    return window.postMessage({});
    """.format(json.dumps(message)))


def set_anti_captcha_api_key(browser, api_key: str):
    # Go to an empty page to execute an API request to the plugin
    browser.get('https://antcpt.com/blank.html')

    # Set the anti-captcha.com API key
    # replace YOUR-ANTI-CAPTCHA-API-KEY with your hexadecimal key, which can be taken here:
    # https://anti-captcha.com/clients/settings/apisetup
    acp_api_send_request(
        browser,
        'setOptions',
        {'options': {'antiCaptchaApiKey': api_key}}
    )

    # Three seconds pause so the plugin can verify the API KEY on the anti-captcha.com side
    time.sleep(3)


def get_browser_with_plugin_ready(plugin_path: str, driver_path: str, api_key: str):
    # Initiate Chrome options object to be able to connect the extension
    options = webdriver.ChromeOptions()
    # Link to the CRX or ZIP file of the plugin we downloaded earlier
    options.add_extension(plugin_path)

    # Create a Browser object (Chrome Web Driver) passing the path where the driver file was downloaded
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
