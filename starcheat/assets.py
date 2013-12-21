# module for loading/indexing Starbound assets

import os, json, re, pickle

assets_folder = "/opt/starbound/assets"

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
