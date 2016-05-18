import os


class Frames(object):
    def __init__(self, assets):
        self.assets = assets
        self.starbound_folder = assets.starbound_folder

    def is_frames(self, key):
        if key.endswith(".frames"):
            return True
        else:
            return False

    def index_data(self, asset):
        key = asset[0]
        path = asset[1]
        name = os.path.basename(key).split(".")[0]
        asset_type = "frames"

        asset_data = self.assets.read(key, path)

        if asset_data is None:
            return

        if "frameList" in asset_data:
            category = "list"
        elif "frameGrid" in asset_data:
            category = "grid"
        else:
            return

        return (key, path, asset_type, category, name, "")

    def get_all_frames(self):
        """Return a list of every indexed blueprints."""
        c = self.assets.db.cursor()
        q = "select * from assets where type = 'frames' order by name collate nocase"
        c.execute(q)
        return c.fetchall()

    def get_frames(self, name):
        """Return indexed frames data from name."""
        c = self.assets.db.cursor()
        q = "select key, path, category from assets where type = 'frames' and name = ?"
        c.execute(q, (name,))
        meta = c.fetchone()
        if meta is not None:
            frames = self.assets.read(meta[0], meta[1])
            return frames, meta[0], meta[1], meta[2]
        else:
            return None

    def lookup_frame(self, name, frame):
        """Return bounding box for given frame in frames file, allows aliases."""
        frames = self.get_frames(name)
        if frames is None:
            return
        data = frames[0]

        if "aliases" in data and frame in data["aliases"]:
            key = data["aliases"][frame]
        else:
            key = frame

        if frames[3] == "list":
            if key in data["frameList"]:
                return data["frameList"][key]
            else:
                return
        elif frames[3] == "grid":
            size = data["frameGrid"]["size"]
            dimensions = data["frameGrid"]["dimensions"]
            tiles = data["frameGrid"]["names"]

            for y in range(dimensions[1]):
                for x in range(dimensions[0]):
                    if tiles[y][x] == key:
                        rx = x * size[0]
                        ry = y * size[1]
                        return [rx, ry, rx+size[0], ry+size[1]]
