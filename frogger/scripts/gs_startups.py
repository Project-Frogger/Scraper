from typing import Tuple

from bs4 import BeautifulSoup, ResultSet
from bs4.element import Tag

from selenium.webdriver.firefox.webdriver import WebDriver

from frogger.script import Script
from frogger.controller import Controller


class GSStartupsScript(Script):

    _name = "Generation-Startup script"
    _description = "Script for parcing generation-startup.ru"
    _author = "Frogger Team"

    def __init__(self, controller: Controller):
        self.controller = controller
        self.database = controller.event_database

    def get_startups(self, driver: WebDriver) -> ResultSet[Tag]:
        """Parses site `generation-startup.ru` with provided driver and returns raw startups list."""
        driver.get("https://generation-startup.ru/startups/")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        startups = soup.find_all("div", {"class": "main-accelerators__item-wrap"})

        return startups

    def get_parsed_startups(self, startups: ResultSet[Tag]) -> list[Tuple[str, str]]:
        """Parses raw events and returns list with information about event."""
        parsed_startups = []

        for startup in startups:
            name: str = startup.find("div", {"class": "main-accelerators__name"}).get_text()
            link: str = startup.find("a", {"class": "button"}).get('href')

            if link.startswith("/"):
                link = ("https://generation-startup.ru" + link).replace(" ", "%20")

            parsed_startup = (name, link)

            parsed_startups.append(parsed_startup)

        return parsed_startups

    def run(self) -> None:
        self.database.truncate_table("src_gs_startups")
        startups = self.get_startups(self.controller.webdriver)
        startups_parsed = self.get_parsed_startups(startups)
        self.database.insert_list_into_table(
            "src_gs_startups",
            "name, site",
            startups_parsed
        )
        self.database.call_proc("f_get_gs_startups")


def setup(controller: Controller) -> None:
    """Loads Script to controller."""
    controller.install_script(GSStartupsScript(controller))
