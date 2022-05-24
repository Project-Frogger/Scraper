from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager


class Driver:
    """"""

    def __init__(self) -> None:
        self._webdriver = self._create_driver()

    def _create_driver(self) -> WebDriver:
        options = Options()
        options.set_headless()
        return webdriver.Firefox(options=options)

    def close(self) -> None:
        self._webdriver.close()

    def quit(self) -> None:
        self._webdriver.quit()

    def execute(self, javascript: str) -> None:
        self._webdriver.execute(javascript)
