from selenium.webdriver import FirefoxOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

from frogger.database import EventDatabase
from frogger.script import Script
from frogger.script_manager import ScriptManager


class Controller:
    """Main controller."""

    def __init__(self):
        service = Service(GeckoDriverManager(log_level=30).install())
        options = FirefoxOptions()
        options.add_argument("--headless")

        self.webdriver = Firefox(service=service, options=options)
        self.event_database = EventDatabase()
        self.script_manager = ScriptManager()

        self._installed_scripts: list[Script] = []
        self._run_scripts_setups()

    def _run_scripts_setups(self) -> None:
        """
        Runs scrupts setup into Controller.

        This methods walks thought script manager's
        scripts, gets their setup function
        that calls `install_script` function.
        """
        for script in self.script_manager.scripts_set:
            setup_func = self.script_manager.get_setup_func(script)
            setup_func(self)

    def install_script(self, script: Script) -> None:
        """Adds script object to _installed_scripts list."""
        self._installed_scripts.append(script)

    def run_script_by_index(self, index: int) -> None:
        """Runs script by provided index from `_installed_scripts`."""
        script = self._installed_scripts[index]
        script.run()

    def run_every_script(self):
        """Runs every script from `_installed_scripts`"""
        for script in self._installed_scripts:
            script.run()
