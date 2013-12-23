"""
Config file module
"""

import configparser

config_file =  configparser.ConfigParser()
# TODO: work out what to set this to
config_file.read("starcheat.ini")
config = config_file["starcheat"]
