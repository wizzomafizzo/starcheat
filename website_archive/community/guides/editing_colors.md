Starbound has (so far) two general ways to change the colors of items. Both work on the same general idea: give Starbound a list of colors in groups of two, Starbound will go through and replace the color on the left with the color on the right in the given image/item.

# Replace strings

When you refer to an image asset by its path in an item, you can add a special bit of text on the end to instruct Starbound to replace colors in the image. An example image key in an item looks a bit like this:

```json
    "image": "/items/swords/randomgenerated/candycane/handle/1.png?replace;676767=756257;b1b1b1=a18d7f;e9e9e9=e0c7b5;f5e458=eb3f3f;624122=5b5b5b;886337=7f7e7d"
```

It's not too difficult once you know how it works. First, here is how you can turn it into something more readable...

Find the question mark (?) in the image path. Everything to the left of the question mark is the path to the image asset, everything to the right is the replace string. We want the replace string, so now we end up with this:

```
    replace;676767=756257;b1b1b1=a18d7f;e9e9e9=e0c7b5;f5e458=eb3f3f;624122=5b5b5b;886337=7f7e7d
```

Each argument in the replace string is divided with a semicolon (;), so we can split that up now into a list:

*  replace

*  676767=756257

*  b1b1b1=a18d7f

*  e9e9e9=e0c7b5

*  f5e458=eb3f3f

*  624122=5b5b5b

*  886337=7f7e7d

That looks a little better. The first item in the list tells Starbound what the stuff after the question mark actually does. In this case, it's a replace string, but there can be other types. Everything after that is instructions on what colors to replace with what.

Colors are represented as hex strings, similar to in HTML, but with the standard hash (#) dropped off at the start. You can use a website like http://www.colorpicker.com/ or an image editor to calculate new colors.

The color on the left is the one in the original image that you want to replace, the color on the right is what you want to replace it with. Don't forget you can unpack assets if you need to reference the original image.

FIXME Pretty sure you're allowed to put multiple replace string on a single image. Might need to expand on that.

# Color options



