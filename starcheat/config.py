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

STARCHEAT_VERSION = "0.11 (Enraged Koala)"
CONFIG_VERSION = 7
ini_file = os.path.join(config_folder, "starcheat.ini")

class Config():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_folder = config_folder
        self.ini_file = ini_file
        self.CONFIG_VERSION = CONFIG_VERSION

    def read(self, option):
        self.config.read(self.ini_file)
        return self.config["starcheat"][option]

    def has_key(self, option):
        self.config.read(self.ini_file)
        return option in self.config["starcheat"]

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
            "config_version": CONFIG_VERSION
        }

        self.config["starcheat"] = defaults

        self.config.write(open(ini_file, "w"))

    def remove_config(self):
        """Delete/reset the current config file if possible."""
        try:
            os.remove(ini_file)
        except FileNotFoundError:
            pass

    def detect_starbound_folder(self):
        known_locations = [
            'C:\Program Files\Steam\SteamApps\common\Starbound',
            'C:\Program Files (x86)\Steam\SteamApps\common\Starbound',
            os.path.expanduser("~/Library/Application Support/Steam/SteamApps/common/Starbound"),
            os.path.expanduser("~/.steam/root/SteamApps/common/Starbound"),
            os.path.expanduser("~/.steam/steam/SteamApps/common/Starbound")
        ]

        if platform.system() == "Windows":
            import winreg
            try:
                steam = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Valve\Steam")
                steam_path = os.path.normpath(winreg.QueryValueEx(steam, "SteamPath")[0])
                known_locations.append(os.path.join(steam_path, "SteamApps", "common", "Starbound"))
                steam.Close()
            except OSError:
                pass

        for filename in known_locations:
            if os.path.isdir(filename):
                return filename
        return ""
