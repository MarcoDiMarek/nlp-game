import asyncio
import pprint
from abc import abstractmethod
import random
from typing import Generator

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
    def __init__(self, name, *to_possess) -> None:
        """Controller name, object(s) to possess."""
        super().__init__(name)
        self.controlled = set(to_possess)
        all(self.possess(self.controlled))

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

##EXAMPLE
# class someobj():
#     def __init__(self, controller=None) -> None:
#         self.controller=controller
#         if self.controller:
#             controller.possess(self)
    
# real_obj = someobj()
# controller = Controller("Player Controller")
# to_possess = [real_obj, "a"]
# all(controller.possess(*to_possess))
# failed = [gobj[0] for gobj in zip(to_possess, controller.possess(*to_possess)) if not gobj[1]]
# print(controller)