from abc import abstractmethod, ABCMeta

class GameObject:
    gameInstance = None
    def __init__(self, name=None, level=None, metaclass=ABCMeta) -> None:
        self._name = name
        self.level = level

    def getname(self) -> str:
        return self._name or str(id(self))

    def rename(self, name):
        self._name = name
        # call an "event" to notify subscribers (if implemented)

    def BeginPlay(self, level) -> bool:
        """Prepare object right before the first run of the Update loop.
        Now objects know they can access each other since all have been loaded."""
        self.level = level
        # print(f"{self._name} started")
        # print(f"FINISHED {self._name}")
        return True

    @staticmethod
    @abstractmethod
    def generate_parser():
        return None

    @classmethod
    def fromconfig(self, args, parser) -> None:
        return None

class Controller(GameObject, metaclass=ABCMeta):
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

    @abstractmethod
    def update(self, args) -> bool:
        return False

class PlayerController(Controller):
    def __init__(self, name, controls_functions={}, *to_possess) -> None:
        super().__init__(name, *to_possess)
        self.controls_functions = controls_functions

    @classmethod
    def fromstring(self, name, controls_functions, *to_possess):
        ctrl_fx = {control:getattr(self, fx_name) for control, fx_name in controls_functions.items()}
        return PlayerController(name, ctrl_fx, *to_possess)

    def update(self, args=[]) -> bool:
        if args:
            try:
                return self.controls_functions[args[0]](args) is True
            except KeyError:
                print("You typed something we did not understand. Type \"commands\" for help.")
                return False
        return False

    def go(self, args=[]):
        for actor in self.controlled:
            pass
        pass
    
    def take(self, args=[]):
        pass

    def release(self, args=[]):
        pass

    def show(self, args=[]):
        pass

    def open(self, args=[]):
        pass

    def commands(self, args=[]):
        pass

    def holding(self, args=[]):
        pass

    def quit(self, args=[]):
        pass

class Player(GameObject):
    def __init__(self, name="player", controller=None, location = None) -> None:
        super().__init__(name)
        self.controller = controller
        self.inventory = []
        self.location = location
        if self.controller:
            controller.possess(self)