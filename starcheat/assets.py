# module for loading/indexing Starbound assets

import os, json, re, sqlite3

from config import config

# Regular expression for comments
comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)

# source: http://www.lifl.fr/~riquetd/parse-a-json-file-with-comments.html
def parse_json(filename):
    """ Parse a JSON file
        First remove comments and then use the json module package
        Comments look like :
            // ...
        or
            /*
            ...
            */
    """
    with open(filename) as f:
        content = ''.join(f.readlines())

        ## Looking for comments
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)

        # Return json file
        return json.loads(content)

def init_db():
    tables = ("create table items (name text, path text, category text, icon text)",)
    db = sqlite3.connect(config["assets_db"])
    c = db.cursor()
    for q in tables:
        c.execute(q)
    db.commit()
    db.close()

class Items():
    def __init__(self):
        self.items_folder = config["assets_folder"] + "/items"
        self.ignore_items = ".*\.(png|config|frames|generatedsword|generatedgun|generatedshield|coinitem)"

        new = False
        try:
            open(config["assets_db"])
        except FileNotFoundError:
            new = True
            init_db()

        self.db = sqlite3.connect(config["assets_db"])

        if new:
            self.add_all_items()

    def file_index(self):
        index = []
        for root, dirs, files in os.walk(self.items_folder):
            for f in files:
                if re.match(self.ignore_items, f) == None:
                    index.append((f, root))
        print("Found " + str(len(index)) + " files")
        return index

    def add_all_items(self):
        index = self.file_index()
        items = []
        print("Indexing item assets", end="")
        for f in index:
            filename = f[1] + "/" + f[0]
            try:
                info = parse_json(filename)
            except ValueError:
                continue

            try:
                name = info["itemName"]
            except KeyError:
                try:
                    name = info["name"]
                except KeyError:
                    name = info["objectName"]

            path = filename
            category = f[0].partition(".")[2]

            try:
                icon = f[1] + "/" + info["inventoryIcon"]
            except KeyError:
                icon = ""

            items.append((name, path, category, icon))
            print(".", end="")
        c = self.db.cursor()
        q = "insert into items values (?, ?, ?, ?)"
        c.executemany(q, items)
        self.db.commit()
        print("Done!")

    def get_all_items(self):
        c = self.db.cursor()
        c.execute("select * from items")
        return c.fetchall()

    def get_item(self, name):
        c = self.db.cursor()
        c.execute("select * from items where name = ?", (name,))
        meta = c.fetchone()
        item = parse_json(meta[1])
        return item
