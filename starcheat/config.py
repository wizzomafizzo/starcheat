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

if os.path.isdir(config_folder) == False:
    os.mkdir(config_folder)

ini_file = os.path.join(config_folder, "starcheat.ini")
# make a special case for this since it is referenced before the main window
log_folder = os.path.join(config_folder, "logs")

class Config():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_folder = config_folder
        self.ini_file = ini_file

    def read(self, option):
        self.config.read(self.ini_file)
        return self.config["starcheat"][option]

    def set(self, option, value):
        self.config.read(ini_file)
        self.config["starcheat"][option] = value
        self.config.write(open(ini_file, "w"))

    def create_config(self, starbound_folder=None):
        # Default values
        # TODO: we can do some auto-detection here
        if starbound_folder == None:
            starbound_folder = self.detect_starbound_folder()

        assets_folder = os.path.join(starbound_folder, "assets")

        # TODO: not 100% sure on the Windows and Mac ones
        if platform.system() == "Linux":
            folder = "linux" + platform.architecture()[0].replace("bit", "")
            player_folder = os.path.join(starbound_folder, folder, "player")
        else:
            player_folder = os.path.join(starbound_folder, "player")

        backup_folder = os.path.join(config_folder, "backups")
        make_backups = "no"
        update_timestamps = "no"
        assets_db = os.path.join(config_folder, "assets.db")

        defaults = {
            "starbound_folder": starbound_folder,
            "assets_folder": assets_folder,
            "player_folder": player_folder,
            "backup_folder": backup_folder,
            "assets_db": assets_db,
            "make_backups": make_backups,
            "update_timestamps": update_timestamps,
        }

        self.config["starcheat"] = defaults

        self.config.write(open(ini_file, "w"))

    def detect_starbound_folder(self):
        # TODO: add common locations for all OSs
        known_locations = [
            "/opt/starbound"
        ]

        for filename in known_locations:
            if os.path.isdir(filename):
                return filename
        return ""
