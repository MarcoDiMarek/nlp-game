# def ReadIgnore(file_path, marker="#", sections=["#CommandBindings"]):
#     with open(file_path) as f:
#         ignoring = False
#         for line in f:
#             command = line.strip()
#             if not ignoring:
#                 if command in sections:
#                     ignoring = True
#                     continue
#                 else:
#                     yield command
#             elif command not in sections and marker in command:
#                 ignoring = False
#                 continue

# # commands = [command for command in ReadIgnore("level.txt", sections=["#CommandBindings"])]
# # print(commands)

# from GameObjects import Door
# import enum

# class DoorState(enum.Enum):
#     open = 1
#     closed = 2
#     locked = 3

# # print(DoorState.closed)
# # print(DoorState["closed"])
# # print(DoorState(2))
# print([DoorState(e).name for e in DoorState])

# from colorama import init, Fore, Back, Style
# init(convert=True)
# print(Fore.RED + 'some red text')
# print(Back.GREEN + 'and with a green background')
# print(Style.DIM + 'and in dim text')
# print(Style.RESET_ALL)
# print('back to normal now')
# input("")