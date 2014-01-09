"""
Config file module

Config and environment stuff goes here, try keep OS-specific functions here too
"""

import configparser, os, platform

if platform.system() == "Windows":
    config_folder = os.path.join(os.path.expandvars("%APPDATA%"), "starcheat")
elif platform.system() == "Darwin":
    config_folder = os.path.expanduser("~/Library/Application Support/starcheat")
else:
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

defaults = {
    "assets_folder": assets_folder,
    "player_folder": player_folder,
    "backup_folder": backup_folder,
    "assets_db": assets_db,
    "make_backups": make_backups,
    "update_timestamps": update_timestamps,
    "log_folder": log_folder
}

class Config():
    def __init__(self):
        self.config = configparser.ConfigParser()

        try:
            open(ini_file)
        except FileNotFoundError:
            self.create_config()

    def read(self, option):
        self.config.read(ini_file)
        try:
            return self.config["starcheat"][option]
        except KeyError:
            # if the config setting doesn't exist, attempt to set a default val
            self.set(option, defaults[option])
            return self.config["starcheat"][option]

    def set(self, option, value):
        self.config.read(ini_file)
        self.config["starcheat"][option] = value
        self.config.write(open(ini_file, "w"))

    def create_config(self):
        self.config["starcheat"] = defaults

        if os.path.isdir(config_folder) == False:
            os.mkdir(config_folder)

        self.config.write(open(ini_file, "w"))
