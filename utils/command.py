from inspect import signature, Signature, Parameter
from typing import List, Mapping, Optional
from asyncio import iscoroutinefunction


class FunctionIsNotCoroutine(Exception):
    pass


class EditCommand:
    """A command that the user can execute using the /edit/ endpoint."""

    def __init__(
            self,
            function,
            *,
            name: Optional[str] = None,
            parameters: Optional[List[Mapping[str, str]]] = None,
            description: Optional[str] = None,
    ):
        if not iscoroutinefunction(function):
            raise FunctionIsNotCoroutine

        self._function = function

        self._name = name
        self._parameters = parameters
        self._description = description

    @property
    def function(self):
        return self._function

    @property
    def _signature(self) -> Signature:
        return signature(self.function)

    @property
    def name(self) -> str:
        return self._name or self.function.__name__ or None

    @property
    def description(self) -> str:
        return self._description or self.function.__doc__ or None

    @property
    def parameters(self) -> List[Mapping[str, str]]:
        if self._parameters is None:
            params_list = []
            params = dict(self._signature.parameters)
            del params["fp"]

            for parameter in params.values():
                param_dict = {"name": parameter.name}

                if parameter.annotation is not Parameter.empty:
                    try:
                        param_dict["type"] = parameter.annotation.__name__
                    except AttributeError:
                        param_dict["type"] = None

                params_list.append(param_dict)
        else:
            params_list = None

        return self._parameters or params_list or None

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

    def command(
            self,
            *,
            name: Optional[str] = None,
            parameters: Optional[List[Mapping[str, str]]] = None,
            description: Optional[str] = None,
    ):
        """Decorator to add a command to the command list.

        A function should have one argument named fp, which is a file pointer to the file that should be edited.
        This should be the first positional argument."""

        def decorator(function):
            self.append(
                EditCommand(
                    function,
                    name=name,
                    parameters=parameters,
                    description=description
                )
            )

        return decorator
