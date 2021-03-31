import asyncio
import pprint
from abc import abstractmethod
import random
from sys import modules
from typing import Generator

class GameObject:
    def __init__(self, name=None) -> None:
        self.name = name

    def getname(self) -> str:
        return self.name or str(id(self))

    def rename(self, name):
        self.name = name
        # call an event to notify subscribers (if implemented)

    def BeginPlay(self, level) -> bool:
        """Prepare object right before the first run of the Update loop.
        Now objects know they can access each other since all have been loaded."""
        self.level = level
        print(f"{self.name} started")
        print(f"FINISHED {self.name}")
        return True

    @staticmethod
    @abstractmethod
    def generate_parser():
        return None

    @classmethod
    def fromconfig(self, args, parser) -> None:
        return None

class Controller(GameObject):
    """A class to be inherited by AI controllers or Player Controllers."""
    def __init__(self, name, *to_possess) -> None:
        """Controller name, object(s) to possess."""
        super().__init__(name)
        self.controlled = set(to_possess)
        all(self.possess(*self.controlled))

    def possess(self, *to_possess):
        """An object / a list thereof to possess.
        Yield True on successs."""
        for gobj in to_possess:
            try:
                old_controller = gobj.controller
                if old_controller:
                    old_controller.dispossess(old_controller)
                gobj.controller = self
                self.controlled.add(gobj)
                yield True
            except AttributeError:
                yield False
        yield False

    def dispossess(self, *to_dispossess):
        """An object / a list thereof to dispossess."""
        for gobj in to_dispossess:
            if gobj in self.controlled:
                self.controlled.remove(gobj)
                gobj.controller = None
                yield True
            else:
                yield False
        yield False

class PlayerController(Controller):
    def __init__(self, name, controls_functions={}, *to_possess) -> None:
        super().__init__(name, *to_possess)
        self.controls_functions = controls_functions

    @classmethod
    def fromstring(self, name, controls_functions, *to_possess):
        ctrl_fx = {control:getattr(self, fx_name) for control, fx_name in controls_functions.items()}
        return PlayerController(name, ctrl_fx, *to_possess)

    def go(self):
        pass
    
    def take(self):
        pass

    def release(self):
        pass

    def show(self):
        pass

    def open(self):
        pass

    def commands(self):
        pass

    def holding(self):
        pass

    def quit(self):
        pass

# #EXAMPLE
# class someobj():
#     def __init__(self, controller=None) -> None:
#         self.controller=controller
#         if self.controller:
#             controller.possess(self)
# pl = someobj()
# pc = PlayerController.fromstring("Nice controller", {"m":"move"}, pl)
