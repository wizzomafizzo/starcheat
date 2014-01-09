#!/usr/bin/env python3

import logging, os, datetime, sys, traceback
from PyQt5.QtWidgets import QMessageBox

import config, gui

log_folder = config.Config().read("log_folder")
log_file = os.path.join(log_folder,
                        "starcheat_" + datetime.date.today().isoformat() + ".log")

def exception_handler(type, value, tb):
    for err in traceback.format_exception(type, value, tb):
        logging.debug(err)
    traceback.print_exception(type, value, tb)
    # simple dialog for now, need at least some feedback
    dialog = QMessageBox()
    msg = "Oops, starcheat has crashed.\n\n"
    for line in traceback.format_exception(type, value, tb):
        msg += line
    dialog.setText(msg)
    dialog.exec()
    # TODO: crash report qt dialog

if not os.path.isdir(log_folder):
    os.mkdir(log_folder)

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
