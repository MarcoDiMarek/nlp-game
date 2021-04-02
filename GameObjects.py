from Components import GameObject
import argparse
import enum

class Room(GameObject):
    def __init__(self, name, doors=None) -> None:
        super().__init__(name)
        self.doors = doors or {}
    
    @staticmethod
    def generate_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument("name", default=None)
        return parser

    @classmethod
    def fromconfig(self, args, parser, level_objs):
        values = parser.parse_args(args)
        return Room(values.name)

class Door(GameObject):
    class DoorState(enum.Enum):
        OPEN = 1
        CLOSED = 2
        LOCKED = 3

    def __init__(self, name, state, keys=None) -> None:
        super().__init__(name)
        # self.directions = directions
        self.state = state
        # self.rooms = rooms
        self.keys = keys

    @staticmethod
    def generate_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument("--name", default=None)
        parser.add_argument("directions")
        parser.add_argument("state", default="closed", 
                            choices=[Door.DoorState(e).name for e in Door.DoorState])
        parser.add_argument("room1")
        parser.add_argument("room2")
        parser.add_argument("--keys", nargs="*", action="append", required=False, type=str)
        return parser

    @classmethod
    def fromconfig(self, args, parser, level_objs):
        v = parser.parse_args(args)
        directions = v.directions.split("-")
        rooms = v.room1, v.room2
        v.name = v.name or f"Door {'_'.join(rooms)}"
        for index, room in enumerate(rooms):
            level_objs[Room.__name__][room].doors[directions[index]] = self
        return Door(v.name, Door.DoorState[v.state], v.keys)

class Item(GameObject):
    def __init__(self, name, location, stationary, action) -> None:
        super().__init__(name)
        self.location = location
        self.stationary = stationary
        self.action = action

    @staticmethod
    def generate_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument("name", default=None)
        parser.add_argument("room")
        parser.add_argument("type", default="STATIONARY")
        parser.add_argument("--action", required=False, nargs="?")
        return parser

    @classmethod
    def fromconfig(self, args, parser, level_objs):
        v = parser.parse_args(args)
        v.type = v.type.upper() == "STATIONARY"
        return Item(v.name, v.room, v.type, v.action)