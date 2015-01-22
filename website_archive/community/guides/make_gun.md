(credit to Lolazaurus on reddit)

A lot of modding for guns is simply changing numbers. You can see them when you double click on any gun. If you want to make a new gun, spawn in any generated gun like "avianblaster" or "commonassaultrifle" the same way you would spawn in the cape or any other item on StarCheat. Some important values you can change are:


*  **classMultiplier**: How much energy your gun takes to shoot. 0 = no energy

*  **fireTime**: How fast your gun shoots

*  **firePosition**: Where your gun spawns its muzzle flash and projectiles

*  **drawables**: How your gun looks. You can use any image file in the game! The position of the image is determined by x and y coordinates. You can also change the color of the images but I never bothered to figure that out. Feel free to open up other guns and see how they're drawn.

*  **handPosition**: How your character holds the gun and where their hand goes on it using x and y coordinates.

*  **inventoryIcon**: Basically the same thing as drawables, only it's what the icon in your inventory looks like.

*  **muzzleEffect**: The little poof your gun gives off when it fires. You can use any .animation file in the assets. Here is also where what sound your gun makes is. You can use any .wav or .ogg sound effect file in your assets.

*  **projectile**: Where you can determine how much damage your gun does, how fast the bullets go, and how long the bullets stay on screen among many other options. "level" is your gun's damage, and "power" is a multiplier to that damage. (makes gun generation easier I guess) You can also add "speed" and "timeToLive" which is your projectile speed and how long your projectile stays on the screen, respectively.

*  **projectileType**: Your gun can shoot just about anything! Anything that has a .projectile file can be shot out of your gun. Look in your asset files for some cool stuff. Warning: there's a lot of evil stuff you can shoot out of your gun. Please respect servers and other players.

*  **shortDescription**: Your gun's name.

*  **spread**: How many projectiles your gun fires at once. Don't go too crazy or your computer will hate you.

*  **twoHanded**: True or False, pretty self-explanatory. Want to shoot two rapid-firing shotguns at once? Well now you can!

Now if you create errors by using incorrect formatting or spelling file names wrong you will either crash the game or cause your item to turn into a useless "Perfectly Generic Item" so make sure you spell things right and look at other guns to see how their formatting works.
