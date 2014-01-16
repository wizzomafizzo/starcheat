#!/usr/bin/env python3

import logging, os, datetime, sys, traceback
from PyQt5.QtWidgets import QMessageBox

import config, gui

log_file = os.path.join(config.log_folder,
                        "starcheat_" + datetime.date.today().isoformat() + ".log")

def exception_handler(type, value, tb):
    for err in traceback.format_exception(type, value, tb):
        logging.debug(err)
    logging.debug(config.Config().read("assets_folder"))
    logging.debug(config.Config().read("player_folder"))
    traceback.print_exception(type, value, tb)
    # simple dialog for now, need at least some feedback
    dialog = QMessageBox()
    dialog.setText("Oops, starcheat has crashed.")
    msg = "Take a screenshot of this message if you'd like to report it in the discussion thread.\n\n"
    for line in traceback.format_exception(type, value, tb):
        msg += line
    dialog.setInformativeText(msg)
    dialog.exec()

if not os.path.isdir(config.log_folder):
    os.mkdir(config.log_folder)

def main():
    # TODO: set logging level in ini and cmd line
    # TODO: probably can save some file space omitting the date in timestamp
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format='%(asctime)s: %(message)s')

    sys.excepthook = exception_handler

    logging.info('starcheat init')

    gui.MainWindow()

if __name__ == "__main__":
    main()
