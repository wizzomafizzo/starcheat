
## Unpacking Starbound assets

starcheat now natively reads .pak files and unpacked Starbound assets including mods. You shouldn't need to do any of this to make starcheat work.

### Windows

 1.  Press the Windows key and R (Win+R) to bring up the **Run...** dialog
 2.  Enter the following text into the prompt and press Enter:

    `"C:\Program Files (x86)\Steam\SteamApps\common\Starbound\win32\asset_unpacker.exe" "C:\Program Files (x86)\Steam\SteamApps\common\Starbound\assets\packed.pak" "C:\Program Files (x86)\Steam\SteamApps\common\Starbound\assets"`

If Steam is not installed to the default location, change the paths above to match your Steam/Starbound location.

### Linux

**NOTE:** If you're on 32 bit, change the path to asset_unpacker.

In a terminal:

    $ cd ~/.steam/root/SteamApps/common/Starbound
    $ linux64/asset_unpacker assets/packed.pak assets/

### Mac

In a terminal:

    $ cd ~/Library/Application\ Support/Steam/SteamApps/common/Starbound
    $ Starbound.app/Contents/MacOS/asset_unpacker assets/packed.pak assets

