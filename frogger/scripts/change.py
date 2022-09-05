import time

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
        self.sleep_time = 3
        self.url = "https://changellenge.com"

    def truncate_table(self) -> None:
        """Truncates table in database."""

        connection, cursor = self.controller.create_db_conn_and_cursr()
        cursor.execute("truncate table src_change")
        connection.commit()
        cursor.close()
        connection.close()

    def load_full_page(self, driver: WebDriver) -> None:
        """
        Loads full page content.
        """
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(self.sleep_time)  # Allows to escape anitbot trigger

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def get_events(self, driver: WebDriver) -> ResultSet[Tag]:
        """Gets events from page."""        
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
                link = self.url + link

            day = event.find("div", {"class": "new-events-card__data-checkin"}).find("span").get_text()

            month = event.find("div", {"class": "new-events-card__data-checkin"}) \
                .find("div", {"class": "new-events-card__date"}) \
                .find("div", {"class": "new-events-card__date"}) \
                .get_text()

            event_type = event.find("span", {"class": "new-events-card__type"}).get_text()

            parsed_events.append((name, day, link, event_type, month))

        return parsed_events

    def load_to_database(self, events: list) -> None:
        "Loads provided events to database."

        connection, cursor = self.controller.create_db_conn_and_cursr()

        command = """
        INSERT INTO src_change
        (name, event_day, site, event_type, event_month)
        VALUES (%s, %s, %s, %s, %s)
        """

        for event in events:
            cursor.execute(command, event)
            connection.commit()

        cursor.callproc("f_get_change")
        connection.commit()

        cursor.close()
        connection.close()

    def run(self) -> None:
        """Runs script."""
        self.truncate_table()
        
        self.controller.driver.get(f"{self.url}/event")
        
        print("change: >>>>>>>>>>>> loading main page <<<<<<<<<<<<")
        self.load_full_page(self.controller.driver)
        
        print("change: >>>>>>>>>>>> getting events <<<<<<<<<<<<")
        events = self.get_events(self.controller.driver)
        
        print("change: >>>>>>>>>>>> parsing events <<<<<<<<<<<<")
        parsed_events = self.parse_events(events)

        print("change: >>>>>>>>>>>> getting events <<<<<<<<<<<<")
        self.load_to_database(parsed_events)


def setup(controller: Controller) -> None:
    """Loads Script to controller."""
    controller.add_script(ChangeScript(controller))
