import atexit
from selenium import webdriver


class MyFirefox(webdriver.Firefox):
    def quit(self):
        webdriver.Firefox.quit(self)
        self.session_id = None

FIREFOX = MyFirefox()


def check_driver():
    global FIREFOX
    try:
        FIREFOX.title
    except ConnectionRefusedError:
        FIREFOX = MyFirefox()


def open_url(url):
    check_driver()
    FIREFOX.get(url)


def run_code(text):
    check_driver()
    script = 'return ({})()'.format(text)
    return FIREFOX.execute_script(script)

@atexit.register
def q():
    FIREFOX.quit()

