"""
Config file module
"""

import configparser, os, platform

if platform.system() == "Windows":
    config_folder = os.path.join(os.path.expandvars("%APPDATA%"), "starcheat")
else:
    # TODO: this will work on mac but isn't really correct
    config_folder = os.path.expanduser("~/.starcheat")

ini_file = os.path.join(config_folder, "starcheat.ini")

# Default values
# TODO: we can do some auto-detection here
assets_folder = ""
player_folder = ""

backup_folder = os.path.join(config_folder, "backups")
make_backups = "no"
update_timestamps = "no"
assets_db = os.path.join(config_folder, "assets.db")

# TODO: now that people can change options while running there needs to be
#       a function to read direct from the config
class Config():
    def __init__(self):
        self.config_file = configparser.ConfigParser()

        try:
            open(ini_file)
        except FileNotFoundError:
            self.create_config()

        self.config_file.read(ini_file)

    def read(self):
        return self.config_file["starcheat"]

    def create_config(self):
        self.config_file["starcheat"] = {
            "assets_folder": assets_folder,
            "player_folder": player_folder,
            "backup_folder": backup_folder,
            "assets_db": assets_db,
            "make_backups": make_backups,
            "update_timestamps": update_timestamps
        }

        if os.path.isdir(config_folder) == False:
            os.mkdir(config_folder)

        self.config_file.write(open(ini_file, "w"))

    def write(self, config):
        self.config_file["starcheat"] = config
        self.config_file.write(open(ini_file, "w"))
