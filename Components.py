from abc import abstractmethod, ABCMeta

class GameObject:
    gameInstance = None
    def __init__(self, name=None, level=None, visible=True, metaclass=ABCMeta) -> None:
        self._name = name
        self.level = level
        self.visible = visible

    def getname(self) -> str:
        return self._name or str(id(self))

    def rename(self, name):
        self._name = name
        # call an "event" to notify subscribers (if implemented)

    def BeginPlay(self, level) -> bool:
        """Allows to prepare object right before the first run of the Update loop.
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
                return self.controls_functions[args[0]](self, args) is True
            except KeyError:
                print("You typed something we did not understand. Type \"commands\" for help.")
                return False
        return False

    def go(self, args=[]):
        try:
            direction = args[1]
        except IndexError:
            print("You need to provide direction in which to go.")
            return
        for actor in self.controlled:
            room_name = actor.location
            room = actor.level.LevelObjects["Room"][room_name]
            try:
                door = room.doors[direction]
            except KeyError:
                print("No door in this direction.")
                continue
            if not door.is_open():
                print("The door is not open!")
                return
            other_room = [room for room in door.rooms if room != room_name][0]
            actor.location=other_room
            self.show()
    
    def take(self, args=[]):
        actor = next(iter(self.controlled))
        try:
            name = args[1]
        except IndexError:
            print("No item provided.")
            return
        room = actor.level.LevelObjects["Room"][actor.location]
        items = room.items
        item = room.GetItem(name)
        if item is not None and item.visible:
            if item.action not in ["use", "drink"]:
                print("Cannot take this with me.")
                return
            actor.inventory.append(item)
            item.visible = False
            items.remove(item)
            print("You took the", item.getname())
        else:
            print("Item was not found in the room.")

    def move(self, args=[]):
        actor = next(iter(self.controlled))
        try:
            name = args[1]
        except IndexError:
            print("No item provided.")
            return
        room = actor.level.LevelObjects["Room"][actor.location]
        item = room.GetItem(name)
        if item:
            item.move()
        else:
            print("Item was not found in the room.")

    def release(self, args=[]):
        actor = next(iter(self.controlled))
        try:
            name = args[1]
        except IndexError:
            print("No item provided.")
            return
        room = actor.level.LevelObjects["Room"][actor.location]
        item = actor.find_in_inventory(name)
        if item:
            room.items.add(item)
            actor.inventory.remove(item)
            item.visible = True
            print("You released the", item.getname(), "in the",actor.location)
        else:
            print("Item was not found in the inventory.")

    def turn(self, args=[]):
        actor = next(iter(self.controlled))
        try:
            name = args[1]
        except IndexError:
            print("No item provided.")
            return
        item = actor.find_in_inventory(name)
        if item.action == "turn":
            print(item.reaction)
        else:
            print("Cannot turn this.")

    def show(self, args=[]):
        for actor in self.controlled:
            room_name = actor.location
            room = actor.level.LevelObjects["Room"][room_name]
            print(f"You are in the room {room_name}.", 
                  f"There are following items here: {', '.join([item.getname() for item in room.items if item.visible])}",
                  f"and {len(room.doors)} doors: {', '.join(room.doors.keys())}", sep="\n")

    def open(self, args=[]):
        try:
            direction = args[1]
        except IndexError:
            print("You need to provide direction in which a door is to be open.")
            return
        for actor in self.controlled:
            room_name = actor.location
            room = actor.level.LevelObjects["Room"][room_name]
            try:
                door = room.doors[direction]
            except KeyError:
                print("No door in given direction.")
                return
            door.open()

    def unlock(self, args=[]):
        try:
            direction = args[1]
        except IndexError:
            print("You need to provide direction in which a door is to be unlocked.")
            return
        for actor in self.controlled:
            room_name = actor.location
            room = actor.level.LevelObjects["Room"][room_name]
            try:
                door = room.doors[direction]
            except KeyError:
                print("No door in given direction.")
                return
            door.unlock(actor)

    def drink(self, args=[]):
        try:
            for actor in self.controlled:
                item = actor.find_in_inventory(args[1])
                if item.action == "drink":
                    print(item.reaction)
                else:
                    print("Cannot drink this.")
        except:
            print("This item is not in your inventory yet.")

    def commands(self, args=[]):
        print(f"Possible commands are: {', '.join(self.controls_functions.keys())}")

    def holding(self, args=[]):
        items = [item.getname() for actor in self.controlled for item in actor.inventory]
        print(f"Items in your inventory: {', '.join(items) if items else 'nothing'}")
        pass

    def quit(self, args=[]):
        pass

class Player(GameObject):
    def __init__(self, name="player", level=None, controller=None, location = None) -> None:
        super().__init__(name, level=level)
        self.controller = controller
        self.inventory = []
        self.location = location
        if self.controller:
            controller.possess(self)

    def find_in_inventory(self, name):
        for item in self.inventory:
            if item.getname() == name:
                return item
        print(f"Not found match {item.getname()}, {name}")
        return None