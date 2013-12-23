# module for loading/indexing Starbound assets

import os, json, re, sqlite3

assets_folder = "/opt/starbound/assets"
assets_db = "./assets.db"

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

class Items():
    def __init__(self):
        self.items_folder = assets_folder + "/items"
        self.ignore_items = ".*\.(png|config|frames|generatedsword|generatedgun|generatedshield|coinitem)"

        new = False
        try:
            open(assets_db)
        except FileNotFoundError:
            new = True

        self.db = sqlite3.connect(assets_db)
        if new:
            self.create_db()

    def create_db(self):
        q = "create table items (name text, path text, category text, icon text)"
        c = self.db.cursor()
        c.execute(q)
        self.db.commit()

    def file_index(self):
        index = []
        for root, dirs, files in os.walk(self.items_folder):
            for f in files:
                if re.match(self.ignore_items, f) == None:
                    index.append((f, root))
        return index

    def add_all_items(self):
        index = self.file_index()
        items = []
        c = self.db.cursor()
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
        q = "insert into items values (?, ?, ?, ?)"
        c.executemany(q, items)
        self.db.commit()

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

if __name__ == "__main__":
    items = Items()
    items.add_all_items()
    print(items.get_all_items())
