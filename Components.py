from Engine import Game
import asyncio
import pprint
from abc import abstractmethod
import random

class GameObject:
    def __init__(self, name=None) -> None:
        self.name = name

    def getname(self) -> str:
        return self.name or str(id(self))

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
    def __init__(self, name, to_possess=[]) -> None:
        """Controller name, objects to possess."""
        super().__init__(name)
        self.controlled = set(to_possess) # allow both a list and a single obj
        self.possess(self.controlled)

    def possess(self, to_possess) -> bool:
        """An element / a list thereof to possess."""
        gobjs = set(to_possess)
        for gobj in gobjs:
            try:
                old_controller = gobj.controller
                if old_controller:
                    old_controller.dispossess(old_controller)
                gobj.controller = self
                yield True
            except AttributeError:
                yield False

    def dispossess(self, to_dispossess) -> bool:
        """An element / a list thereof to dispossess."""
        gobjs = set(to_dispossess)
        for gobj in gobjs:
            if gobjs in self.controlled:
                self.controlled.remove(gobj)
                yield True
            else:
                yield False

class Collider:
    """Template class to be inherited by specific types of colliders.
       
       Game objects that have their own colliders can collide with each other.
       
       Relative Locaion to Object = (0,0) center (pivot) of the object"""

    def __init__(self, RelativeLocToObject, active=False):
        self.location = (0,0) # 0,0 center of the object
        self.active = active
    pass

class BoxCollider(Collider):
    def __init__(self, RelativeLocToObject, RelativeSizeToObject):
        super().__init__(self, RelativeLocToObject)
        self.boundaries = (
                        # Top Left
                        (RelativeLocToObject[0]-RelativeSizeToObject[0]/2, 
                        RelativeLocToObject[1]-RelativeSizeToObject[1]/2),
                        # Top Rigth
                        (RelativeLocToObject[0]+RelativeSizeToObject[0]/2, 
                        RelativeLocToObject[1]-RelativeSizeToObject[1]/2),
                        # Bottom Left
                        (RelativeLocToObject[0]-RelativeSizeToObject[0]/2, 
                        RelativeLocToObject[1]+RelativeSizeToObject[1]/2),
                        # Bottom Right
                        (RelativeLocToObject[0]+RelativeSizeToObject[0]/2, 
                        RelativeLocToObject[1]+RelativeSizeToObject[1]/2)
                    )
    def __str__(self) -> str:
        boundaries = zip(("Top Left", "Top Right", "Bottom Left", "Bottom Right"), self.boundaries)
        return pprint.pformat(list(boundaries))

