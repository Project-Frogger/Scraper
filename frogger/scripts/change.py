import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from bs4 import BeautifulSoup, ResultSet
from bs4.element import Tag

from frogger.controller import Controller
from frogger.script import Script


class ChangeScript(Script):

    _name = "Changellenge.com script"
    _description = "Script for parsing Changellenge.com"
    _author = "Frogger Team"

    def __init__(self, controller: Controller):
        self.controller = controller

    def load_all_events(self, driver: WebDriver) -> None:
        """Loads additional events in page for full loading."""

        while True:
            try:
                driver.find_element(By.CLASS_NAME, "new-events__load_more").click()
            except NoSuchElementException:
                break
            time.sleep(5)

    def get_events(self, driver: WebDriver) -> ResultSet[Tag]:
        """Gets events from page."""
        driver.get("https://changellenge.com/event/")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        events = soup.find("ul", {"class": "new-events__tab new-events__tab--active"}) \
            .find_all("div", {"class": "new-events-card__content"})
        return events

    def parse_events(self, events: ResultSet[Tag]) -> list:
        """Parses events."""

        parsed_events = []

        for event in events:
            name = event.find("h4",   {"class": "new-events-card__title"}).get_text()

            link = event.find("a").get("href")
            if link[0:8] != "https://" and link[0:7] != "http://":
                link = "https://changellenge.com" + link

            day = event.find("div", {"class": "new-events-card__data-checkin"}).find("span").get_text()

            month = event.find("div", {"class": "new-events-card__data-checkin"}) \
                .find("div", {"class": "new-events-card__date"}) \
                .find("div", {"class": "new-events-card__date"}) \
                .get_text()

            event_type = event.find("span", {"class": "new-events-card__type"}).get_text()

            parsed_events.append((name, day, link, event_type, month))

        return parsed_events

    def run(self) -> None:
        """Runs script."""
        self.controller.event_database.truncate_table("src_change")
        self.load_all_events(self.controller.webdriver)
        events = self.get_events(self.controller.webdriver)
        events_parsed = self.parse_events(events)
        self.controller.event_database.insert_list_into_table(
            "src_change",
            "name, event_day, site, event_type, event_month",
            events_parsed
        )
        self.controller.event_database.call_proc("f_get_change_event")


def setup(controller: Controller) -> None:
    """Loads Script to controller."""
    controller.install_script(ChangeScript(controller))
