from os import execlpe


class LevelLoader:
    @staticmethod
    def LoadRoom(args):
        print(f"{LevelLoader.LoadRoom.__name__} received {args}")
    @staticmethod
    def LoadDoor(args):
        print(f"{LevelLoader.LoadDoor.__name__} received {args}")
    @staticmethod
    def LoadItem(args):
        print(f"{LevelLoader.LoadItem.__name__} received {args}")
    @staticmethod
    def LoadGameState(args):
        print(f"{LevelLoader.LoadGameState.__name__} received {args}")

    LoadingFunctions = {
        # keyword : (function, parser)
        "room" : LoadRoom.__func__,
        "door" : LoadDoor.__func__,
        "item" : LoadItem.__func__,
        "start" : LoadGameState.__func__
    }

    def __init__(self, CustomLoadingFunctionsBinding=None):
        self.CustomLoadingFunctionsBinding = CustomLoadingFunctionsBinding

    def LoadLevel(self, full_file_path):
        bindings = self.CustomLoadingFunctionsBinding if self.CustomLoadingFunctionsBinding else LevelLoader.LoadingFunctions

        with open(full_file_path) as f:
            for line in f:
                # Split splits by spaces by default,
                # It is mentioned explicitly if this default ever changes
                args = line.split(" ")
                try:
                    bindings[args[0]]([arg.strip() for arg in args[1:]])
                except KeyError:
                    continue


# Loader = LevelLoader()
# Loader.LoadLevel("level.txt")

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
        args = command_string.split(self.separator)
        try:
            self.bindings[args[0]]([arg.strip() for arg in args[1:]])
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
        self.handler(args, self.parser)

    __call__ = parse


def dummy(args, parser):
    print("dummy called")
    print(args)
    print("parser: ", parser)

def parser():
    print("parser created")

fxpair = FxParserPair(dummy, parser)

handler = CommandHandler({"shit" : fxpair}, "Unrecognized command", True)

handler.parse("no big")