from typing import Tuple

from bs4 import BeautifulSoup, ResultSet
from bs4.element import Tag

from selenium.webdriver.firefox.webdriver import WebDriver

from frogger.script import Script
from frogger.controller import Controller


class GSStartupsScript(Script):

    _name = "Generation-Startup script."
    _description = "Script for parcing generation-startup.ru"
    _author = "Frogger Team"

    def __init__(self, controller: Controller):
        self.controller = controller
        self.sleep_time = 3
        self.url = "https://generation-startup.ru/startups/"

    def truncate_table(self) -> None:
        """Truncates table for RBScript."""
        connection, cursor = self.controller.create_db_conn_and_cursr()
        cursor.execute("truncate table src_gs_startups")
        connection.commit()
        cursor.close()
        connection.close()

    def get_startups(self, driver: WebDriver) -> ResultSet[Tag]:
        """Parses site `generation-startup.ru` with provided driver and returns raw startups list."""
        driver.get(self.url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        soup = BeautifulSoup(driver.page_source, "html.parser").find("div", {"class": "main-accelerators__wrapper--left"})
        startups = soup.find_all("div", {"class": "main-accelerators__item-wrap"})

        return startups

    def get_parsed_startups(self, startups: ResultSet[Tag]) -> list[Tuple[str, str]]:
        """Parses raw events and returns list with information about event."""
        parsed_startups = []

        for startup in startups:
            name: str = startup.find("div", {"class": "main-accelerators__name"}).get_text()
            
            
            link: str = startup.find("a", {"class": "button"})
            if link is not None:
                link: str = startup.find("a", {"class": "button"}).get('href')

                if link.startswith("/"):
                    link = ("https://generation-startup.ru" + link).replace(" ", "%20")

            parsed_startup = (name, link)
            parsed_startups.append(parsed_startup)

        return parsed_startups

    def send_to_database(self, parsed_startups: list[Tuple[str, str]]) -> None:
        """Sends startup's information to database."""
        connection, cursor = self.controller.create_db_conn_and_cursr()
        insert_startup_command = """
        INSERT INTO src_gs_startups
        (name, site)
        VALUES (%s, %s)
        """

        for startup in parsed_startups:
            cursor.execute(insert_startup_command, startup)

        cursor.callproc("f_get_gs_startups")
        connection.commit()

        cursor.close()
        connection.close()

    def run(self) -> None:
        self.truncate_table()
        
        print("gs_startups: >>>>>>>>>>>> getting events <<<<<<<<<<<<")
        startups = self.get_startups(self.controller.driver)
        
        print("gs_startups: >>>>>>>>>>>> parsing events <<<<<<<<<<<<")
        startups_parsed = self.get_parsed_startups(startups)
        
        print("gs_startups: >>>>>>>>>>>> sending events to database <<<<<<<<<<<<")
        self.send_to_database(startups_parsed)


def setup(controller: Controller) -> None:
    """Loads Script to controller."""
    controller.add_script(GSStartupsScript(controller))
