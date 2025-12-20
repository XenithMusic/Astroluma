Root: `{}`

Python syntax is used for types.


`design`: object
-
`species:str`
- Determines the player's species.

The remainder of the parameters here are species specific.

`traits`: object
-
`max_health:int`
- Determines the player's maximum health.

`base_speed:int`
- Determines how fast the player is in tiles/second

`base_attack:int`
- Determines how strong the player's attack is.

`modifiers`: object
-
`attack_mod:float`
- A multiplier to attack damage.

`speed_mod:float`
- A multiplier to speed.

`health:int`
- How much health the player currently has. Yes, this is in `modifiers`, cry about it. I might move it later.