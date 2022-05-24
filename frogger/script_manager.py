import importlib
import inspect
import pkgutil

from importlib.machinery import ModuleSpec
from typing import Iterator

from frogger import scripts


class ScriptManager:

    def __init__(self) -> None:
        self.scripts_set = self.fetch_scripts()

    def walk_scripts(self) -> Iterator[str]:
        """
        Walks thought script's folder and returns Iterator with paths.

        If module starts with `_` - we skipping this file.
        """

        def on_error(name: str):
            raise ImportError(name=name)

        def unqualify(name: str) -> str:
            """Return an unqualified name given a qualified module/package `name`."""
            return name.rsplit(".", maxsplit=1)[-1]

        for module in pkgutil.walk_packages(scripts.__path__, f"{scripts.__name__}.", onerror=on_error):
            if unqualify(module.name).startswith("_"):
                continue

            if module.ispkg:
                imported = importlib.import_module(module.name)
                if not inspect.isfunction(getattr(imported, "setup", None)):
                    continue

            yield module.name

    def fetch_scripts(self) -> set[str]:
        """Loads all known scripts."""
        return set(self.walk_scripts())

    def get_setup_func(self, script: str):
        spec: ModuleSpec = importlib.util.find_spec(script)
        lib = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(lib)

        setup_func = getattr(lib, "setup")
        return setup_func

    def load_script(self, script_path: str) -> None:
        """
        Loads script by provided `script_path`.

        Path shoul looks like frogger.AAA.BBB.CCC
        """
        spec: ModuleSpec = importlib.util.find_spec(script_path)
        lib = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(lib)

        setup_func = getattr(lib, "setup")
        setup_func(self)
