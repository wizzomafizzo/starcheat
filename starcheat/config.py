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

log_folder = os.path.join(config_folder, "logs")

class Config():
    def __init__(self):
        self.config = configparser.ConfigParser()

        try:
            open(ini_file)
        except FileNotFoundError:
            self.create_config()

    def read(self, option=None):
        self.config.read(ini_file)
        if option != None:
            return self.config["starcheat"][option]
        else:
            return self.config["starcheat"]

    def create_config(self):
        self.config["starcheat"] = {
            "assets_folder": assets_folder,
            "player_folder": player_folder,
            "backup_folder": backup_folder,
            "assets_db": assets_db,
            "make_backups": make_backups,
            "update_timestamps": update_timestamps,
            "log_folder": log_folder
        }

        if os.path.isdir(config_folder) == False:
            os.mkdir(config_folder)

        self.config.write(open(ini_file, "w"))

    def write(self, config):
        self.config["starcheat"] = config
        self.config.write(open(ini_file, "w"))
