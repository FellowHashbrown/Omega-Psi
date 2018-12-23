from util.file.database import loop

from functools import partial
import discord, os, requests, traceback

DISCORD_BOT_ORG_API = "https://discordbots.org/api/bots/503804826187071501/votes"

async def sendMessage(client, origMessage, *, message = None, embed = None, filename = None, plain = False):
    """A utility method to send a message to a channel that automatically handles exceptions.\n

    origMessage - The original Discord Message (automatically handles whether to send to use or channel)\n

    Keyword Arguments:\n
     - message - A regular message to send.\n
     - embed - An Embed to send in a Discord Message.\n
     - filename - A file to send given a filename.\n
    """

    if type(origMessage) == discord.TextChannel:
        channel = origMessage
    else:
        channel = origMessage.channel

    # Try sending a message
    try:

        # Message is a regular message
        if message != None:
            return await channel.send(message)
        
        # Message is an Embed
        elif embed != None:
            return await channel.send(embed = embed)
        
        # Message is a filename
        elif filename != None:
            return await channel.send(file = discord.File(filename))
    
    except:
        error = traceback.format_exc()
        await sendErrorMessage(client, error)

async def sendErrorMessage(client, message):
    """A utility method to send an error message to the test server.\n

    message - The message to send.\n
    """

    await getChannel(client,
        os.environ["DISCORD_TEST_SERVER_ID"],
        os.environ["DISCORD_TEST_CHANNEL_ID"]
    ).send("```python\n" + message + "```")

def getChannel(client, serverId, channelId):
    """A utility method that retrieves a Discord Channel given the serverId and channelId.\n

    client - The Discord Client to find the server from.\n
    serverId - The ID of the Discord Server to look in.\n
    channelId - The ID of the Discord Channel to get.\n
    """

    # Iterate through servers the bot is in
    for server in client.guilds:
        if server.id == int(serverId):

            # Iterate through channels the bot has access to
            for channel in server.channels:
                if channel.id == int(channelId):
                    return channel

def getErrorMessage(commandObject, errorType):
    """Returns a Discord Embed object for an error type given.

    Parameters:
        commandObject: The Command to get the error from.
        errorType: The type of error to return.
    
    Returns:
        embed (discord.Embed)
    """
        
    return discord.Embed(
        title = "Error",
        description = commandObject.getErrorMessage(errorType),
        colour = 0xFF0000
    )

async def didAuthorVote(discordUser):
    """Returns whether or not the Discord User voted for Omega Psi on discordbots.org
    """

    # Get request
    response = await loop.run_in_executor(None,
        partial(
            requests.get,
            DISCORD_BOT_ORG_API,
            headers = {
                "Authorization": os.environ["DISCORD_BOT_ORG_TOKEN"]
            }
        )
    )
    voters = response.json()

    return any(voter["id"] == str(discordUser.id) for voter in voters)