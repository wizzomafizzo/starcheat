#!/usr/bin/env python3

import logging, logging.handlers, os, sys, traceback, platform
from PyQt5.QtWidgets import QMessageBox

import config, gui.mainwindow

# set up starcheat internal logging
log_file = os.path.join(config.config_folder, "starcheat.log")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
rotate = logging.handlers.RotatingFileHandler(log_file,
                                               maxBytes=1024*1000,
                                               backupCount=5)
rotate.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
logger.addHandler(rotate)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))
logger.addHandler(console)

# set up Qt crash dialog
def crash_gui(error):
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Critical)
    dialog.setText("Oops, starcheat has crashed.")
    detail = """
<html><head/><body>
<p>To report this error, click <strong>Show Details...</strong> and post the crash report it displays to the starcheat <a href="http://community.playstarbound.com/index.php?threads/starcheat-player-save-editor-and-python-library.60174/">discussion thread</a>.</p>
</body></html>
"""
    dialog.setInformativeText(detail)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.setDetailedText(error)
    dialog.exec()

def exception_handler(type, value, tb):
    for err in traceback.format_exception(type, value, tb):
        logging.debug(err)

    try:
        starbound_folder = config.Config().read("starbound_folder")
    except KeyError:
        starbound_folder = None

    if starbound_folder is None:
        logging.debug("No Starbound folder is set!")
    else:
        logging.debug("Starbound folder: %s", starbound_folder)
        logging.debug("Assets folder: %s", config.Config().read("assets_folder"))
        logging.debug("Player folder: %s", config.Config().read("player_folder"))

    traceback.print_exception(type, value, tb)
    # simple dialog for now, need at least some feedback
    msg = ""
    for line in traceback.format_exception(type, value, tb):
        msg += line
    crash_gui(msg)

sys.excepthook = exception_handler

# go starcheat!
def main():
    if ("--version" in sys.argv or "-v" in sys.argv):
        sys.stdout.write("starcheat %s\n" % config.STARCHEAT_VERSION)
        sys.exit(0)

    logging.info("starcheat init")
    logging.info("Version: %s", config.STARCHEAT_VERSION)
    logging.info("Platform: %s", platform.system())
    gui.mainwindow.MainWindow()

if __name__ == "__main__":
    main()
