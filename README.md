# discord_bot_chatter 

![tag:status:status:production](https://raw.githubusercontent.com/PouceHeure/markdown_tags/v1.0/tags/status/status_production/status_production_green.png)

![tag:language:python3](https://raw.githubusercontent.com/PouceHeure/markdown_tags/v1.0/tags/language/python3/python3_blue.png)

## Goal 
Create a way to define and call easily a chatter bot for sending some messages from anyway in your computer. Just need to create config file with some information about your bots and servers and that's all.

For example, you can use a bot during deep-learning training in sending some information about the current train.

## Get started 

### Require 
You have to create a server and bot. 

You can follow these instructions: [https://discordpy.readthedocs.io/en/latest/discord.html](https://discordpy.readthedocs.io/en/latest/discord.html)


### Installation 
Just need to execute the script **install.sh**

```
# go to the root project 
$ ./install.sh
```

### Configuration 

This script need some information like bot token, server id and channel id. The previous script created a json to this location: 
**~/.discord_bot_chatter/config.json**

Find information: 
- bot token: go to your discord developer portail
- ids (inside discord software): 
  - switch your apparence to developer inside discord settings application  
  - right click in your server and select "copy identification"
  - same for channel

You have to fill it, it's really important to follow this pattern: 

```
{
    "bots": {
        "{bot_name}": {
            "token": "{token}"
        }
    }, 
    "servers": {
        "{server_name}": {
            "id": {server_id},
            "channels": {
                "{channel_example}": {channel_id}
            }
        }
    }
}
```

:pencil: change only elements between "{}"

:pencil: you can add more than one bots/servers


### Use 

This is a simple example: 

```
#importation
from discord_bot_chatter import discord_bot_chatter

if __name__ == "__main__":
    bot = discord_bot_chatter.BotChatter(bot_name="BotExample",
                                        server_name="ServerExample",
                                        default_channel_name="channel_example")

    
    bot.send_message(discord_bot_chatter.Message("bonjour 1").to_block_code())
    bot.connect()
    bot.send_message("bonjour 2")
    bot.disconnect()

```


{bot_name},{server_name} and a {default_channel_name} need to be the same name with your config file. 

:pencil: you can stack messages even if the connection isn't done, once the connection is established all previous messages are sent in the same order. 






