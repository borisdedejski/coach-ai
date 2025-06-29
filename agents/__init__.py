import os
import importlib


def auto_register_agents():
    agents_dir = os.path.dirname(__file__)
    for file in os.listdir(agents_dir):
        if file.endswith(".py") and file not in (
            "__init__.py",
            "base.py",
            "registry.py",
            "orchestrator.py",
        ):
            module_name = f"agents.{file[:-3]}"
            importlib.import_module(module_name)


auto_register_agents()
