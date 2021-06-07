import importlib.util
import os
import sys

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


for file in os.listdir("commands/"):
    if file.endswith(".py"):
        full_path = "commands/" + file
        module_name = os.path.splitext(full_path)[0].replace("/", ".")

        module_spec = importlib.util.find_spec(module_name)
        module = importlib.util.module_from_spec(module_spec)

        sys.modules[module_name] = module

        try:
            module_spec.loader.exec_module(module)
        except Exception as error:
            del sys.modules[module_name]
            raise MiscCommandsLoadingFailure(subapp_name=module_name, original=error)

        try:
            module_commands = getattr(module, "commands")
        except AttributeError:
            del sys.modules[module_name]
            raise CommandsModuleMissingEntrypoint(subapp_name=module_name)

        try:
            commands.extend(module_commands)
        except Exception as error:
            del sys.modules[module_name]
            raise MiscCommandsLoadingFailure(subapp_name=module_name, original=error)
