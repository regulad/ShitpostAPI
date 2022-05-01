import importlib.util
import os
import sys
from importlib.machinery import ModuleSpec
from os.path import join, realpath
from pathlib import Path
from types import ModuleType

from utils.command import CommandList

commands = CommandList()


class CommandsLoadingFailure(Exception):
    def __init__(self, *args, subapp_name: str):
        self.subapp_name = subapp_name

        super().__init__(*args)


class CommandsModuleMissingEntrypoint(CommandsLoadingFailure):
    pass


class MiscCommandsLoadingFailure(CommandsLoadingFailure):
    def __init__(self, *args, subapp_name: str, original: Exception):
        self.original = original

        super().__init__(*args, subapp_name=subapp_name)

for file in os.listdir(join(realpath(os.getcwd()), "commands")):
    if file.endswith(".py"):
        full_path: Path = Path(join(realpath(os.getcwd()), "commands", file)).relative_to(Path(realpath(os.getcwd())))
        module_name: str = os.path.splitext(str(full_path))[0].replace(os.sep, ".")

        module_spec: ModuleSpec | None = importlib.util.find_spec(module_name)
        assert module_spec is not None
        module: ModuleType = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module

        try:  # Jank way to import a module. I know not a better way.
            module_spec.loader.exec_module(module)
            module_commands = getattr(module, "commands")
            commands.extend(module_commands)
        except Exception as error:
            del sys.modules[module_name]
            raise MiscCommandsLoadingFailure(subapp_name=module_name, original=error)
