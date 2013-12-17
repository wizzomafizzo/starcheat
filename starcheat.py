#!/usr/bin/python3

import sys

import save_file

if __name__ == '__main__':
    save_filename = sys.argv[1]
    player = save_file.PlayerSave(save_filename)

    #player.data["health"] = (300.0, 300.0) # works for like a second
    player.data["name"] = "PIX HACK1"
    player.data["pixels"] = (123456,)

    for var in save_file.data_format:
        print(var[0], ":", player.data[var[0]])

    print("Exported save file:", player.export_save("test.player"))
    #print(player.export_save())
