import time

from typing import Tuple

from bs4 import BeautifulSoup, ResultSet
from bs4.element import Tag

from selenium.webdriver.firefox.webdriver import WebDriver

from frogger.script import Script
from frogger.controller import Controller


class RBScript(Script):

    _name = "RB script"
    _description = "Script for parcing rb.ru"
    _author = "Frogger Team"

    def __init__(self, controller: Controller):
        self.controller = controller

    def get_events(self, driver: WebDriver) -> ResultSet[Tag]:
        """Parses site rb.ru with provided driver and returns raw events list."""
        driver.get("https://rb.ru/chance/")

        last_height = driver.execute_script("return document.body.scrollHeight;")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(5)

            new_height = driver.execute_script("return document.body.scrollHeight;")

            if new_height == last_height:
                break

            last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        events = soup.find_all("div", {"class": "chance__card"})

        return events

    def get_parsed_events(self, events: ResultSet[Tag]) -> list[Tuple[str, str, str, str, str]]:
        """Parses raw events and returns list with information about event."""
        parsed_events = []

        for event in events:
            name: str = event.find("a", {"class": "chance__card-name-item ng-binding"}).get_text()
            link: str = event.find("a", {"class": "chance__card-name-item ng-binding"}).get('href')
            day: str = event.find("div", {"class": "chance__card-date-number ng-binding"}).get_text()
            month: str = event.find("div", {"class": "chance__card-date-month ng-binding"}).get_text()
            type: str = event.find("div", {"class": "chance__card-name-categ ng-binding"}).get_text()

            parsed_event = (name, day, link, type, month)
            parsed_events.append(parsed_event)

        return parsed_events

    def run(self) -> None:
        self.controller.event_database.truncate_table("src_rb")
        events = self.get_events(self.controller.webdriver)
        events_parsed = self.get_parsed_events(events)
        self.controller.event_database.insert_list_into_table(
            "src_rb",
            "name, event_day, site, event_type, event_month",
            events_parsed
        )
        self.controller.event_database.call_proc("f_get_rb")


def setup(controller: Controller) -> None:
    """Loads Script to controller."""
    controller.install_script(RBScript(controller))
