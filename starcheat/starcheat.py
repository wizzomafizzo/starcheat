#!/usr/bin/env python3

import logging, os, datetime
import config, gui

log_folder = config.Config().read("log_folder")
log_file = os.path.join(log_folder,
                        "starcheat_" + datetime.date.today().isoformat() + ".log")

if not os.path.isdir(log_folder):
    os.mkdir(log_folder)

def main():
    # TODO: set logging level in ini and cmd line
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format='%(asctime)s: %(message)s')

    logging.info('starcheat init')
    gui.MainWindow()

if __name__ == "__main__":
    main()
