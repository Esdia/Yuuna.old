# Yuuna

## DEPRECATED : This is an old version written before the discord.py rewrite. The development has been stopped, please see the [current version](https://github.com/Esdia/Yuuna/tree/master)

Yuuna is a polyvalent discord bot coded in Python by Esdia using Rapptz's discord API Wrapper.\
I took some inspiration from [cookkkie's Mee6](https://github.com/cookkkie/mee6), all credits to him regarding the way I manage my storage system.

### How to add her to a server
Just click on [this link](https://discordapp.com/oauth2/authorize?client_id=424560276277559296&scope=bot&permissions=2146958591) and select your server. You need the *manage server* permission on the server in order to be able to do that. \
By default, Yuuna will get full permissions, but you can remove some to her, just know that the moderation commands, the games and the shop may stop working, depending on which permissions you remove. \
To be fully usable, Yuuna needs those permissions: \
*manage messages*, *manage roles*, *manage channels*, *kick members*, *ban members*.

Details of the needed permissions :
* Purge : Manage messages
* Mute : Manage channels
* Kick : Kick members
* Ban : Ban members
* Shop, autorole and level rewards : Manage roles
* Games (except for Chess) : Manage message (because she will try to remove reactions)


### Yuuna uses :
* [discord.py](https://github.com/Rapptz/discord.py) : Discord API Wrapper for Python by Rapptz
* [aioredis](https://github.com/aio-libs/aioredis) : Redis client library for Python
* [heroku](https://www.heroku.com/) : Web applications host


### What can she do ?
Yuuna is a polyvalent discord bot. All her features are fully detailed in her help command. \
Her command prefix is `y!`. To get started, please use `y!help`. \
Here's a summary of her main features:

1. The bot configuration :
    * You can change Yuuna's command prefix.
    * You can change Yuuna's language between these two : English, French
    * You can disable every command modules (for example you can disable every bank command by using `y!disable [command]`), except for the configuration commands and the help command.
    
2. Moderation commands :
    * purge
    * mute
    * kick
    * ban
    
3. XP system :
    * You can earn XP by talking in the chat. This XP system can be disabled and some channels can be banned from the XP system. 
    * You can set roles to be automatically given to the members when they reach a certain level.
4. Bank and shop system :
    * You can earn Coins by levelling up with the XP system, and use these Coins in a fully customizable shop where you can buy roles.
5. The games: \
    Yuuna comes with a few games : 
    * Tic Tac Toe
    * Black Jack
    * Connect4
    * Chess