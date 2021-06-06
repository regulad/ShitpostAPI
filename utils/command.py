from inspect import signature, Signature, Parameter
from typing import List, Mapping


class EditCommand:
    """A command that the user can execute using the /edit/ endpoint."""

    def __init__(self, function):
        self._function = function

    @property
    def function(self):
        return self._function

    @property
    def _signature(self) -> Signature:
        return signature(self.function)

    @property
    def name(self) -> str:
        return self.function.__name__

    @property
    def description(self) -> str:
        return self.function.__doc__ or "None provided."

    @property
    def _parameters(self) -> Mapping[str, Parameter]:
        return self._signature.parameters

    @property
    def parameters(self) -> List[dict]:
        params_list = []
        params = dict(self._parameters)
        del params["fp"]

        for parameter in params.values():
            param_dict = {"name": parameter.name}

            if parameter.annotation is not Parameter.empty:
                param_dict["type"] = parameter.annotation.__name__

            params_list.append(param_dict)

        return params_list

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"

    def __dict__(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class CommandList(list):
    """A list that holds and registers commands."""

    def command(self):
        """Decorator to add a command to the command list.

        A function should have one argument named fp, which is a file pointer to the file that should be edited.
        This should be the first positional argument."""

        return lambda function: self.append(EditCommand(function))
