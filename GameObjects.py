from Components import GameObject
import argparse
import enum

class Room(GameObject):
    def __init__(self, name, visible, doors=None, items=None) -> None:
        super().__init__(name, visible=visible)
        self.doors = doors or {}
        self.items = items or set([])
    
    @staticmethod
    def generate_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument("name", default=None)
        parser.add_argument("--hidden", action="store_true")
        return parser

    @classmethod
    def fromconfig(self, args, parser, level_objs):
        values = parser.parse_args(args)
        return Room(values.name, not values.hidden)

    def GetItem(self, name):
        for item in self.items:
            if item.getname() == name:
                return item
        return None

class Door(GameObject):
    class DoorState(enum.Enum):
        OPEN = 1
        CLOSED = 2
        LOCKED = 3

    def __init__(self, name, rooms, visible, state, keys=None) -> None:
        super().__init__(name, visible=visible)
        self.rooms = rooms
        self.state = state
        self.keys = keys

    def is_open(self) -> bool:
        return self.state == Door.DoorState.OPEN

    def open(self):
        if self.state == Door.DoorState.LOCKED:
            print("The door is locked.")
            return False
        elif self.state == Door.DoorState.OPEN:
            print("The door was already open.")
            return False
        else:
            self.state = Door.DoorState.OPEN
            return True

    def unlock(self, player):
        if self.state != Door.DoorState.LOCKED:
            print("The door is NOT locked.")
            return False
        else:    
            for key in self.keys:
                if not player.find_in_inventory(*key):
                    print("You need key(s)!")
                    return False
            self.state = Door.DoorState.CLOSED
            print("Door is now unlocked.")
            return True
        
        

    @staticmethod
    def generate_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument("--name", default=None)
        parser.add_argument("directions")
        parser.add_argument("state", default="closed", 
                            choices=[Door.DoorState(e).name for e in Door.DoorState])
        parser.add_argument("room1")
        parser.add_argument("room2")
        parser.add_argument("--hidden", action="store_true")
        parser.add_argument("--keys", nargs="*", action="append", required=False, type=str)
        return parser

    @classmethod
    def fromconfig(self, args, parser, level_objs):
        v = parser.parse_args(args)
        directions = v.directions.split("-")
        rooms = v.room1, v.room2
        v.name = v.name or f"Door {'_'.join(rooms)}"
        door = Door(v.name, rooms, not v.hidden, Door.DoorState[v.state], v.keys)
        for index, room in enumerate(rooms):
            level_objs[Room.__name__][room].doors[directions[index]] = door
            # pprint(room+f".doors[{directions[index]}]="+door.getname())
        return door

class Item(GameObject):
    def __init__(self, name, visible, location, stationary, action, reaction) -> None:
        super().__init__(name, visible=visible)
        self.location = location
        self.stationary = stationary
        self.action = action
        self.reaction = reaction

    @staticmethod
    def generate_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument("name", default=None)
        parser.add_argument("room")
        parser.add_argument("type", default="STATIONARY")
        parser.add_argument("--hidden", action="store_true")
        parser.add_argument("--then", nargs="*", action="append")
        parser.add_argument("--action", required=False, nargs="?")
        return parser

    @classmethod
    def fromconfig(self, args, parser, level_objs):
        v = parser.parse_args(args)
        v.type = v.type.upper() == "STATIONARY"
        v.then = " ".join([word for sentence in v.then for word in sentence]) if v.then else ""
        item = Item(v.name, not v.hidden, v.room, v.type, v.action, v.then)
        level_objs[Room.__name__][v.room].items.add(item)
        return item

    def move(self):
        if not self.stationary:
            if self.action == "move":
                print("You moved", self.getname(), " but it may once come back cuz the floor is not even.")
                print("Moving heavy stuff is such a muscle donor!")
                milk = self.level.LevelObjects["Item"]["milk"]
                milk.visible = not milk.visible
            elif self.action in ["use","drink"]:
                print("I can take it instead.")
        else:
            print("Can't move this.")
            