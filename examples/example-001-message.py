from discord_bot_chatter import discord_bot_chatter

if __name__ == "__main__":
    bot = discord_bot_chatter.BotChatter(bot_name="BotExample",
                                        server_name="ServerExample",
                                        default_channel_name="channel_example")

    
    bot.send_message(discord_bot_chatter.Message("bonjour 1").to_block_code())
    bot.connect()
    bot.send_message("bonjour 2")
    bot.disconnect()
