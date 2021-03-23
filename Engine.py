from Components import GameObject
import argparse
import asyncio

class PrettySerializable:
    """To be inherited by classes that will make use of config data serialized in our "human readable way"
    that does not correspond to any existing standard (json, xml) etc... """
    @staticmethod
    def FindSection(file_path, marker="#", section=""):
        """Return lines of a section as a generator."""
        with open(file_path) as f:
            saving = False
            for line in f:
                if not saving:
                    if line.strip() == section:
                        saving = True
                        continue
                elif marker in line.strip():
                    break
                else:
                    yield line.strip()

    @staticmethod
    def ParseCommandBindings(lines, module):
        command_fx_dict = {}
        for binding in lines:
            command, reference = binding.split()
            cls = getattr(module, reference)
            pair = FxParserPair(cls.fromconfig, cls.generate_parser)
            command_fx_dict[command] = pair
        return command_fx_dict

    @staticmethod
    def ReadIgnore(file_path, marker="#", sections=[""]):
        """Return lines of all OTHER sections as a generator.
        If no sections provided, returns all lines."""
        with open(file_path) as f:
            ignoring = False
            for line in f:
                command = line.strip()
                if not ignoring:
                    if command in sections:
                        ignoring = True
                        continue
                    else:
                        yield command
                elif command not in sections and marker in command:
                    ignoring = False
                    continue

class Game(PrettySerializable):
    def __init__(self, first_level, controls={}) -> None:
        self.controls = controls
        self.active_level = first_level
        success = self.BeginPlay()
        print(success)
        # loop = asyncio.get_event_loop()
        # results = loop.run_until_complete(asyncio.wait([(loop.run_in_executor(None, obj.BeginPlay, first_level)) for obj in first_level.LevelObjects.values()]))
        # print(results)

    @classmethod
    def fromconfig(self, full_file_path):
        import GameObjects
        lines = Game.FindSection(full_file_path, section="#Controls")
        controls = Game.ParseCommandBindings(lines, GameObjects)
        level = Level.LoadLevel(full_file_path)
        return Game(level, controls)

    def BeginPlay(self) -> bool:
        loop = asyncio.get_event_loop()
        level = self.active_level
        functions = [(loop.run_in_executor(None, obj.BeginPlay, level)) 
                    for obj in level.LevelObjects.values()]
        results = loop.run_until_complete(asyncio.gather(*functions))
        return False not in results

    def update(self):
        pass

class Level(PrettySerializable):
    def __init__(self, LevelObjects={}):
        self.LevelObjects = LevelObjects

    async def BeginPlay(self):
        functions = [obj.BeginPlay(self) for obj in self.LevelObjects.values()]
        return await asyncio.gather(*functions) 

    @classmethod
    def LoadLevel(self, full_file_path, command_fx_dict={}, Objects={}, exceptions=False, separator = " "):
        """command_fx_dict : Additional command bindings.
        Objects : Tries to migrate existing objects into the new level together with the level's objects.
        Exceptions : Show exception if command parsing fails. Does NOT prevent exceptions when instantiating
        fails."""
        import GameObjects
        bindings = Level.FindSection(full_file_path, section="#CommandBindings")
        command_fx_dict = Level.ParseCommandBindings(bindings, GameObjects)        
        handler = CommandHandler(command_fx_dict, exceptions=exceptions, separator=separator)
        lines = Level.ReadIgnore(full_file_path, sections=["#CommandBindings"])
        LevelObjects = {item.getname() : item 
                        for item in (handler.parse(line) for line in lines) if item is not None}
        return Level({**Objects, **LevelObjects})

class CommandHandler:
    def __init__(self, command_fx_pairs, error_msg="", exceptions=False, separator = " ") -> None:
        """command_fx_pairs = command names with respective Function Parser Pairs 
        (= functions paired with argparse).
        {"command" : FxParserPair}

        error_msg = a custom error to be displayed to the user,
        not the exception message
        """
        self.bindings = command_fx_pairs
        self.separator = separator if separator else " "
        self.error_msg = error_msg
        self.exceptions = exceptions
    
    def parse(self, command_string):
        args = command_string.strip().split(self.separator)
        try:
            return self.bindings[args[0]](args[1:])
        except KeyError as error:
            if self.error_msg:
                print(self.error_msg)
            if self.exceptions:
                raise KeyError(f"Unrecognized command {args[0]}") from error

class FxParserPair:
    def __init__(self, function, argparse_creator_fx) -> None:
        """Generates and stores the argument parser by calling
        the argparse creator function.
        The parser is later used by the function passed as argument here."""
        self.handler = function
        self.parser = argparse_creator_fx()

    def parse(self, args):
        return self.handler(args, self.parser)

    __call__ = parse

# lvl = Level.LoadLevel("level.txt")
# print(lvl)

game = Game.fromconfig("level.txt")
input("press enter to quit")