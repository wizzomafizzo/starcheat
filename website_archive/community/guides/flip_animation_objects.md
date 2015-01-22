(by healthire)

This is a method I have devised through hours and hours of breaking the animation system.
 
The problem this solves is that offsets of animationParts or placement of objects get messed up when you place the object facing left (flipped).
 
Some terms I will use that are important:
 

*  **Object origin:** The {0,0} position for your *object*. This is the position that will be returned by entity.position()

*  **Animation origin:** The {0,0} position for your *animation*, this is only used for offsets in the .animation file
 
# Step 1

 
First you have to determine where you want your object origin. I.e. where in the object you want your 0 position.

The default here is bottom left (0,0), but you might want it in the middle.
 
The importance of this is that it changes which position in your object that entity.position() will return.
 
How you shift this is by using the imagePosition parameter. This will set an object origin in the bottom left:

```json
	"image" : "objectsprite.png",
	"imagePosition" : [0, 0]
```

This will set an object origin in the middle, if objectsprite.png is 16x16 pixels:

```json	
	"image" : "objectsprite.png",
	"imagePosition" : [-8, -8]
```

Note that I use negative offsets, because you're shifting the *image* position, not the actual origin position.
 
# Step 2

 
All animation parts that should flip nicely must be set to:

```json	
	"centered" : true
```

In the animation file.
 
You should now consider your *animation* origin to be the middle center of your sprite, and set all your offsets relative to that.
 
#  Step 3

Here's the (somewhat) tricky part. There's an animationPosition parameter in the .object file.

This can be used to move the position of the visible object after you place it.

This should obviously match up with the placement you see in object preview (which you set in imagePosition).
 
Let's say the object origin is the bottom left.

But since we've set stuff as centered, our animation origin will be in the center of the sprite.
Which means the sprite will be drawn with its center in the animation origin,
meaning it's probably halfway into the ground and shifted to the left.
 
This is fixable by doing:
 
 ```json
	"animationPosition" : [8, 8]
```

Which moves the visual for the object 8 pixels (half the width) to the right, and 8 pixels (half the height) up.

Meaning it's placed just like you placed your object in preview mode.
 
If your object origin is in the middle of the object (you set [-8,-8] as your imagePosition),
and your animation origin is in the middle of your object, they should just match up.
This means you do:

```json
	"animationPosition" : [0, 0]
```

And it should be placed correctly both in preview and when placed.
 
# TL;DR

 1.  Make imagePosition what you want it to be. (changes where object origin is)
 2.  Use centered : true unless you're sure you don't want to (srsly, just do it)
 3.  Offset animationParts relative to the CENTER of the object in your .animation file
 4.  Adjust animationPosition to make the placed position correct
