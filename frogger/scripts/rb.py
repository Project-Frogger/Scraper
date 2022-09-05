import json
from urllib.request import Request, urlopen
from itertools import count

from frogger.script import Script
from frogger.controller import Controller


class RBScript(Script):

    _name = "RB script."
    _description = "Script for parcing rb.ru"
    _author = "Frogger Team"

    def __init__(self, controller: Controller):
        self.controller = controller

    def truncate_table(self) -> None:
        """Truncates table for RBScript."""
        connection, cursor = self.controller.create_db_conn_and_cursr()
        cursor.execute("truncate table src_rb")
        connection.commit()
        cursor.close()
        connection.close()

    def get_events(self) -> list[dict]:
        """Parses site rb.ru api returns raw events list."""  
        events = []
        for i in count(1):
            req = Request(
                url=f'https://rb.ru/api/chance/list/?page={i}&limit=32&orphans=5', 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response = urlopen(req).read()
            response_json = json.loads(response)

            events.extend(response_json.get('project_list'))
            if response_json.get('num_pages') == i:
                return events


    def get_parsed_events(self, events: list[dict]) -> list[tuple[str, str, str, str]]:
        """Parses raw events and returns list with information about event."""
        parsed_events = []

        for event in events:         
            name: str = event.get('name')
            link: str = event.get('url')
            date: str = event.get('stop_dt')
            type: str = event.get('category').get('name')

            parsed_event = (name, date, link, type)
            parsed_events.append(parsed_event)

        return parsed_events

    def send_to_database(self, parsed_events: list[tuple[str, str, str, str]]) -> None:
        """Sends event's information to database."""
        connection, cursor = self.controller.create_db_conn_and_cursr()
        insert_event_command = """
        INSERT INTO src_rb
        (name, date_from, site, event_type)
        VALUES (%s, %s, %s, %s)
        """

        for event in parsed_events:
            cursor.execute(insert_event_command, event)

        cursor.callproc("f_get_rb")
        connection.commit()

        cursor.close()
        connection.close()

    def run(self) -> None:
        self.truncate_table()
        
        print("rb: >>>>>>>>>>>> getting events <<<<<<<<<<<<")
        events = self.get_events()
        
        print("rb: >>>>>>>>>>>> parsing events <<<<<<<<<<<<")
        events_parsed = self.get_parsed_events(events)
        
        print("rb: >>>>>>>>>>>> sending events to database <<<<<<<<<<<<")
        self.send_to_database(events_parsed)


def setup(controller: Controller) -> None:
    """Loads Script to controller."""
    controller.add_script(RBScript(controller))
