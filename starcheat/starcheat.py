#!/usr/bin/env python3

import logging, os, datetime
import config, gui

log_dir = os.path.join(config.config_folder, "logs")
log_filename = os.path.join(log_dir,
                            "starcheat_" + datetime.date.today().isoformat() + ".log")

if not os.path.isdir(log_dir):
    os.mkdir(log_dir)

def main():
    # TODO: set logging level in ini and cmd line
    logging.basicConfig(filename=log_filename, level=logging.DEBUG,
                        format='%(asctime)s: %(message)s')

    logging.info('starcheat init')
    gui.MainWindow()

if __name__ == "__main__":
    main()
