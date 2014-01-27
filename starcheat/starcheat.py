#!/usr/bin/env python3

import logging, os, datetime, sys, traceback
from PyQt5.QtWidgets import QMessageBox

import config, gui

log_file = os.path.join(config.log_folder,
                        "starcheat_" + datetime.date.today().isoformat() + ".log")

if not os.path.isdir(config.log_folder):
    os.mkdir(config.log_folder)

def main():
    if ("--version" in sys.argv or "-v" in sys.argv):
        sys.stdout.write("starcheat alpha (Furious Koala)\n")
        sys.exit(0)

    # TODO: set logging level in ini and cmd line
    # TODO: probably can save some file space omitting the date in timestamp
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format='%(asctime)s: %(message)s')

    def crash_gui(error):
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Critical)
        dialog.setText("Oops, starcheat has crashed.")
        detail = """<html><head/>
<p>To report this error, click <strong>Show Details...</strong> and post the crash report it displays to the starcheat <a href="http://community.playstarbound.com/index.php?threads/starcheat-player-save-editor-and-python-library.60174/">discussion thread</a>.</p>
</body></html>"""
        dialog.setInformativeText(detail)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.setDetailedText(error)
        dialog.exec()

    def exception_handler(type, value, tb):
        for err in traceback.format_exception(type, value, tb):
            logging.debug(err)
        logging.debug(config.Config().read("assets_folder"))
        logging.debug(config.Config().read("player_folder"))
        traceback.print_exception(type, value, tb)
        # simple dialog for now, need at least some feedback
        msg = ""
        for line in traceback.format_exception(type, value, tb):
            msg += line
        crash_gui(msg)

    sys.excepthook = exception_handler

    logging.info('starcheat init')
    gui.MainWindow()

if __name__ == "__main__":
    main()
