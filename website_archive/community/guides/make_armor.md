# Creating armor and other equipment

Most of the wearable equipment works basically the same. They all have a set of common item options, and most customisation is done by changing what **status effects** apply to the item.


*  **colorOptions:** This works like other color editing parts of Starbound. Color hex values on the left of each pair of colors will replace the color on the right. See [here](editing_colors.md) for how that works.

*  **description:** This is was shows in the item hover description box in your inventory.

*  **dropCollision:** ???

*  **femaleFrames:** Points to the sprite sheets that will be used to render the armor for females. Can be any image but will have hardcoded methods of cropping the spritesheet.

*  **inspectionKind:** Refers to what type of item it is. Not sure how exactly Starbound uses this.

*  **inventoryIcon:** What to show as the inventory icon. If there is something on the end like ":chest" it is referring to what part of the spritesheet to crop.

*  **itemName:** The abase sset's unique ID.

*  **maleFrames:** Same as female frames, but for dudes.

*  **maxStack:** How many of the item you can stack in a single inventory slot.

*  **rarity:** How rare the item is. Mostly just changes the inventory icon border colour.

*  **shortdescription:** The item's name in-game. Different to the asset ID.

*  **statusEffects:** This is where the magic happens.

statusEffects look like this:

```json	
	 [
	   {
	     "amount": 37.5,
	     "kind": "ColdProtection"
	   },
	   {
	     "amount": 160,
	     "kind": "Protection",
	     "level": 34
	   },
	   {
	     "amount": 270,
	     "kind": "healthincrease"
	   }
	 ]
```

Each part in curly braces is a separate status effect, each status effect will be constantly applied to your player. Status effect do LOTS of different things, and take different arguments depending on what they do, so you really need to look through the status effect assets and see what each one does.


*  **kind:** This refers to the status effect ID that will be used. All the status effects are in /statuseffects/ in the Starbound assets. "kind" is usually the statuseffect filename minus the extension.

*  **amount:** This is the most common argument for status effects, but is not required on some. In "healthincrease" for example, it means how many hit point the armor will increase a player's health.

*  **level:** Same as "amount". It's common but will mean different things depending on the statuseffect.

So, let's say we want to make it so the armor will always heal you...

 1.  Look in /statuseffects/ asset folder for something that looks like it might heal you. For this, we can use bandage.statuseffect
 2.  In that file, you can see the "kind" field is "bandage", so we'll use that in our armor.
 3.  In the "primitives" section you can see an amount field. This usually means you can adjust how strong the effect is. We can leave it for now.

So now we have enough to add it. This is what your new statuseffects option will look like:

```json
	 [
	   {
	     "amount": 37.5,
	     "kind": "ColdProtection"
	   },
	   {
	     "amount": 160,
	     "kind": "Protection",
	     "level": 34
	   },
	   {
	     "amount": 270,
	     "kind": "healthincrease"
	   },
	   {
	     "kind": "bandage"
	   }
	 ]
```

Simple as that! Now you can equip your armour and it will be like a bandage is constantly being applied!
