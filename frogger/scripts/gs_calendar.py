import time

from typing import Tuple

from bs4 import BeautifulSoup, ResultSet
from bs4.element import Tag

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException

from frogger.script import Script
from frogger.controller import Controller


class GSStartupsScript(Script):

    _name = "Generation-Startup-Calendar script"
    _description = "Script for parcing generation-startup.ru calendar"
    _author = "Frogger Team"

    def __init__(self, controller: Controller):
        self.controller = controller
        self.database = controller.event_database
        self.sleep_time = 3
        self.url = "https://generation-startup.ru"

    def load_full_page(self, driver: WebDriver, main_page=False) -> None:
        """
        Loads full page content.

        If we parcing main page - set `main_page` to `True` on call.
        """
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(self.sleep_time)  # Allows to escape anitbot trigger

            if main_page:
                try:
                    submit_button = driver.find_element_by_css_selector('.button-add')
                    submit_button.click()
                except ElementNotInteractableException:
                    print("DEBUG: Button not interactable.")
                except NoSuchElementException:
                    print("DEBUG: Button not found.")

                time.sleep(self.sleep_time)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def get_events(self, driver: WebDriver) -> ResultSet[Tag]:
        """Parses site `generation-startup.ru` with provided driver and returns raw events list."""
        driver.get(f"{self.url}/calendar")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        startups = soup.find_all("a", {"class": "events-startups__item-wrap"})
        return startups

    def get_parsed_events(self, driver: WebDriver, events: ResultSet[Tag]) -> list[Tuple[str, str, str, str, str]]:
        """Parses raw events and returns list with information about event."""
        parsed_events = []

        for event in events:
            soup = BeautifulSoup(str(event), "html.parser")
            url = self.url + soup.find("a", {"class": "events-startups__item-wrap"})["href"]
            driver.get(url)

            self.load_full_page(driver)

            event_page = BeautifulSoup(driver.page_source, "html.parser")

            name = event_page.select("h1", {"class": "h1 active"})[0].text.strip()
            grid = event_page.find("div", {"class": "events-detail-info__grid"})

            try:
                date = grid.find("div", {"class": "events-detail-info__item data active"})

                if date is not None:
                    date = grid.find("div", {"class": "events-detail-info__item data active"}) \
                        .findChildren("div")[1].get_text() \
                        .replace("\n", "").replace("  ", "")

                place = grid.find("div", {"class": "events-detail-info__item local active"})
                if place is not None:
                    place = grid.find("div", {"class": "events-detail-info__item local active"}) \
                        .findChildren("div")[1].get_text() \
                        .replace("\n", "").replace("  ", "")

                organisation = grid.find("div", {"class": "events-detail-info__item organizer active"})

                if organisation is not None:
                    organisation = grid.find("div", {"class": "events-detail-info__item organizer active"}) \
                        .findChildren("div")[1].get_text() \
                        .replace("\n", "").replace("  ", "")

                site = grid.find("div", {"class": "events-detail-info__item site active"})
                if site is not None:
                    site = grid.find("div", {"class": "events-detail-info__item site active"}).find("a")['href']
                else:
                    site = event_page.find("a", {"class": "button button--max active"})
                    if site is not None:
                        site = event_page.find("a", {"class": "button button--max active"})['href']

            except TypeError as te:
                print(f"We got a trouble.\n{te}")

            description = event_page.find("div", {"class": "events-detail__content active"}).get_text()

            parsed_event = (name, date, place, site, description)
            parsed_events.append(parsed_event)

        return parsed_events

    def run(self) -> None:
        self.database.truncate_table("table src_gs_calendar")
        self.load_full_page(self.controller.webdriver, True)
        self.get_events(self.controller.webdriver)
        events = self.get_events(self.controller.webdriver)
        events_parsed = self.get_parsed_events(self.controller.webdriver, events)
        self.database.insert_list_into_table(
            "src_gs_calendar",
            "name, event_date, place, site, descr",
            events_parsed
        )
        self.database.call_proc("f_get_gs_calendar")


def setup(controller: Controller) -> None:
    """Loads Script to controller."""
    controller.install_script(GSStartupsScript(controller))
