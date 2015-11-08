"""
Config file module

Config and environment stuff goes here, try keep OS-specific functions here too
"""

import configparser
import os
import platform

if platform.system() == "Windows":
    config_folder = os.path.join(os.path.expandvars("%APPDATA%"), "starcheat")
elif platform.system() == "Darwin":
    config_folder = os.path.expanduser("~/Library/Application Support/starcheat")
else:
    config_folder = os.path.expanduser("~/.starcheat")

if not os.path.isdir(config_folder):
    os.mkdir(config_folder)

STARCHEAT_VERSION = "0.27.1 (Glad Giraffe)"
STARCHEAT_VERSION_TAG = "0.27.1"
CONFIG_VERSION = 15
ini_file = os.path.join(config_folder, "starcheat.ini")


class Config(object):
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
        if "starcheat" in self.config:
            return option in self.config["starcheat"]
        else:
            return False

    def set(self, option, value):
        self.config.read(ini_file)
        self.config["starcheat"][option] = value
        self.config.write(open(ini_file, "w"))

    def create_config(self, starbound_folder=None):
        # Default values
        if starbound_folder is None:
            starbound_folder = self.detect_starbound_folder()

        storage_folder = "giraffe_storage"

        assets_folder = os.path.join(starbound_folder, "assets")
        player_folder = os.path.join(starbound_folder, storage_folder, "player")
        mods_folder = os.path.join(starbound_folder, storage_folder, "mods")
        backup_folder = os.path.join(config_folder, "backups")
        pak_hash = "none"
        check_updates = "yes"
        assets_db = os.path.join(config_folder, "assets.db")

        defaults = {
            "starbound_folder": starbound_folder,
            "assets_folder": assets_folder,
            "player_folder": player_folder,
            "mods_folder": mods_folder,
            "backup_folder": backup_folder,
            "pak_hash": pak_hash,
            "assets_db": assets_db,
            "check_updates": check_updates,
            "config_version": CONFIG_VERSION
        }

        self.config["starcheat"] = defaults

        self.config.write(open(ini_file, "w"))

        if not os.path.isdir(backup_folder):
            os.mkdir(backup_folder)

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
                key = "Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Steam App 211820"
                if platform.machine().endswith('86'):
                    key = "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Steam App 211820"
                starbound_uninstall = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key)
                starbound_path = winreg.QueryValueEx(starbound_uninstall, "InstallLocation")[0]
                known_locations.append(os.path.normpath(starbound_path))
                starbound_uninstall.Close()
            except OSError:
                pass
            try:
                steam = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Valve\\Steam")
                steam_path = os.path.normpath(winreg.QueryValueEx(steam, "SteamPath")[0])
                known_locations.append(os.path.join(steam_path, "SteamApps", "common", "Starbound"))
                steam.Close()
            except OSError:
                pass

        for path in known_locations:
            if os.path.isdir(path) and os.path.isfile(os.path.join(path, "assets", "packed.pak")):
                return path
        return ""
