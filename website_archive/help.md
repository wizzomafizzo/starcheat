This is stuff you can do when starcheat stops working. [Clearing local settings](#reset-all-settings) and checking you did the setup correctly is always a good first step.

**If you've tried all this stuff but starcheat is still broken, please post a bug report in the [discussion thread](http://community.playstarbound.com/index.php?threads/starcheat-player-save-editor-and-python-library.60174/) for support.**

# Known issues

*  If you get a **System Error dialog** as soon as you run starcheat, you probably need [this Windows update](http://www.microsoft.com/en-au/download/details.aspx?id=14632).

*  If you get a message like **no compatible saves** found it means the player folder was not detected properly or you haven't created and players in Starbound yet. To update the player folder location:
    - Open up the options dialog in starcheat (Tools menu > Options)
    - Set the Starbound Folder option to the correct folder
    - Click Save
    - Try open a new player (File menu > Open)

*  If **missing inventory icons** are being displayed, you see **no species** to select or you **can't edit items**; the assets folder location may not have been detected properly:
    - Open up the options dialog in starcheat (Tools menu > Options)
    - Set the Starbound Folder option to the correct one
    - Click Rebuild DB
    - Click Save
    - Restart starcheat

# Reporting a new error

Any other errors or if starcheat doesn't start you can do these steps:
 1.  Follow these instructions and then try run starcheat again
 2.  If that doesn't work, please make a new post in [this thread](http://community.playstarbound.com/index.php?threads/starcheat-player-save-editor-and-python-library.60174/) with the following information:

    * A copy of the latest starcheat logs (instructions to get logs are [here](#how-to-get-logs))
    * A list of any mods installed
    * *(Optional)* A screenshot of the error
    * *(Optional)* A .zip file containing any .player files you're having trouble with

# Troubleshooting steps

## Reset all settings

This will remove all locally stored data for starcheat and force a new setup dialog next run.

### Windows

 1.  Press the Windows key and R (Win+R) to bring up the **Run...** dialog
 2.  Type **`%APPDATA%\starcheat`** and press Enter
 3.  Delete **`assets.db`** and **`starcheat.ini`** from the folder that pops up

### Linux

In a terminal:

    $ rm ~/.starcheat/assets.db
    $ rm ~/.starcheat/starcheat.ini

### Mac

In Finder:
 1.  Open the **Go** menu and click **Go to Folder** (or press Cmd+Shift+G)
 2.  Type **`~/Library/Application Support/starcheat`** and press Enter
 3.  Delete **`assets.db`** and **`starcheat.ini`** from the folder that pops up

## How to get logs

This will point you to where the starcheat logs are stored. If you're trying to report an error, you only need to upload the **`starcheat.log`** file. If you need a place to upload it, use a pastebin site like [dpaste](http://dpaste.com/).

### Windows

 1.  Press the Windows key and R (Win+R) to bring up the **Run...** dialog
 2.  Type **`%APPDATA%\starcheat`** and press Enter

### Linux

In a terminal:

    $ cd ~/.starcheat

### Mac

In Finder:

 1.  Open the **Go** menu and click **Go to Folder** (or press Cmd+Shift+G)
 2.  Type **`~/Library/Application Support/starcheat`** and press Enter
