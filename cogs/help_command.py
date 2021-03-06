from discord import Embed
from discord.ext.commands import HelpCommand, Paginator

from cogs.errors import get_error_message

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

GITHUB_RELEASE = "https://github.com/FellowHashbrown/Omega-Psi/releases/tag/{}"

cogs = {
    "animal": {
        "name": "Animal",
        "emoji": ":unicorn: ",
        "extension": "cogs.animal.animal",
    },
    "code": {
        "name": "Code",
        "emoji": ":keyboard: ",
        "extension": "cogs.code.code"
    },
    "game": {
        "name": "Game",
        "emoji": ":video_game: ",
        "extension": "cogs.game.game"
    },
    "stats": {
        "name": "Stats",
        "emoji": ":clipboard: ",
        "extension": "cogs.stats.stats"
    },
    "insults": {
        "name": "Insult",
        "emoji": ":exclamation: ",
        "extension": "cogs.insults.insults"
    },
    "math": {
        "name": "Math",
        "emoji": ":asterisk: ",
        "extension": "cogs.math.math"
    },
    "music": {
        "name": "Music",
        "emoji": ":musical_note: ",
        "extension": "cogs.music.music"
    },
    "comics": {
        "name": "Comics",
        "emoji": ":notebook: ",
        "extension": "cogs.comics.comics"
    },
    "memes": {
        "name": "Memes",
        "emoji": ":joy: ",
        "extension": "cogs.memes.memes"
    },
    "misc": {
        "name": "Misc",
        "emoji": ":mag: ",
        "extension": "cogs.misc.misc"
    },
    "server": {
        "name": "Server",
        "emoji": ":floppy_disk: ",
        "extension": "cogs.server.server"
    },
    "bot": {
        "name": "Bot",
        "emoji": ":robot: ",
        "extension": "cogs.bot.bot"
    },
    "developer": {
        "name": "Developer",
        "emoji": ":desktop: ",
        "extension": "cogs.developer.developer",
        "hidden": True
    }
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Help(HelpCommand):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def send_error_message(self, error):
        """Sends an error message to the error channel for Omega Psi

        :param error: The error message to display
        """
        await self.context.send(embed = get_error_message(error))

    def command_not_found(self, string):
        """Returns a custom string when a given command is not found in the bot

        :param string: The name of the command that was not found
        """
        return "No command called `{}` found".format(string)
    
    def subcommand_not_found(self, command, string):
        """Returns a custom string when a given subcommand is not found under the given command

        :param command: The command that did not have the specified subcommand
        :param string: The name of the subcommand that was not found
        """
        return "`{}` has no subcommand `{}`".format(command.name, string)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Bot, Cog, Group, and Command Help
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def send_bot_help(self, mapping):
        """Sends a list of cogs in the bot, sorted alphabetically

        :param mapping: A mapping of Cogs and a list of commands in each cog
        """

        # Get the most recent version of Omega Psi
        recent = await database.bot.get_recent_update()

        # Create an embed with a list of cogs and their emojis/help commands
        embed = Embed(
            title = "Omega Psi Commands",
            description = "Below is a list of categories in Omega Psi",
            colour = await get_embed_color(self.context.author)
        ).set_author(
            name = "Version " + recent["version"],
            url = GITHUB_RELEASE.format(recent["version"]),
            icon_url = "https://omegapsi.fellowhashbrown.com/static/logo.png"
        ).set_footer(
            text = "`[]` parameters are optional; `<>` parameters are required"
        )

        # Add fields for each cog in the bot
        #   only add cogs with a name, not None
        for cog in mapping:
            if cog and (
                    (cog.qualified_name != "developer" and
                     await database.bot.is_cog_enabled(cog.qualified_name)) or 
                     await database.bot.is_developer(self.context.author)):
                
                # check if the cog is the music cog and the user is in a private message
                if cog.qualified_name != "music" or self.context.guild:
                    embed.add_field(
                        name = "{} {}".format(
                            cogs[cog.qualified_name]["emoji"],
                            cogs[cog.qualified_name]["name"]
                        ),
                        value = "`{}help {}`".format(
                            await database.guilds.get_prefix(self.context.guild) if self.context.guild else "",
                            cog.qualified_name
                        )
                    )

        await self.context.send(embed = embed)

    async def send_cog_help(self, cog):
        """Sends a list of commands in the specified cog, sorted alphabetically

        :param cog: The cog object to get help for
        """

        # Make sure the user can access this cog
        if ((
                cog.qualified_name != "developer" and 
                await database.bot.is_cog_enabled(cog.qualified_name)
            ) or await database.bot.is_developer(self.context.author)):

            # Filter the commands so the checks are done for each command
            commands = await self.filter_commands(cog.get_commands(), sort = True)
            paginator = Paginator(prefix = "", suffix = "", max_size = 1000)
            
            # Create an embed with a list of commands in the cog
            embed = Embed(
                title = "{} {}".format(
                    cogs[cog.qualified_name]["emoji"],
                    cogs[cog.qualified_name]["name"]
                ),
                description = cog.description,
                colour = await get_embed_color(self.context.author)
            )

            # Only add commands if there are any
            if len(commands) > 0:
                for command in commands:
                    paginator.add_line("`{}{}` - {}".format(
                        await database.guilds.get_prefix(self.context.guild) if self.context.guild else "",
                        command.name,
                        command.description
                    ))
                
                # Add each page in the paginator to the embed
                for i in range(len(paginator.pages)):
                    embed.add_field(
                        name = "Commands",
                        value = paginator.pages[i]
                    )
        # The cog is the developer cog and the user is not a developer
        else:
            embed = get_error_message("You can't access this category!")

        await self.context.send(embed = embed)
    
    async def send_group_help(self, group):
        """Sends the command, and any subcommands, laid out by the specified group
        sorted alphabetically

        :param group: The group object to get help for
        """

        # Run a check on the command to make sure the author can run it
        try:
            await group.can_run(self.context)

            # Filter the subcommands so the checks are done for each subcommands
            commands = await self.filter_commands(group.commands, sort = True)
            paginator = Paginator(prefix = "", suffix = "", max_size = 1000)
            
            # Create an embed to show the command and the subcommands
            embed = Embed(
                title = group.qualified_name,
                description = group.description,
                colour = await get_embed_color(self.context.author)
            )
            
            if len(group.aliases) > 0:
                embed.add_field(
                    name = "Aliases",
                    value = ", ".join([
                        f"`{alias}`"
                        for alias in group.aliases
                    ]),
                    inline = False
                )
            
            # Only add subcommands if there are any
            if len(commands) > 0:
                for command in commands:
                    paginator.add_line("`{}` - {}".format(
                        command.name,
                        command.description
                    ))
                
                # Add each page in the paginator to the embed
                for i in range(len(paginator.pages)):
                    embed.add_field(
                        name = "Subcommands",
                        value = paginator.pages[i]
                    )
        
        # The author can't run it so they can't get help on the command
        except:
            embed = get_error_message("You can't access this command!")
        
        await self.context.send(embed = embed)
    
    async def send_command_help(self, command):
        """Sends help for the specified command

        :param command: The command object to get help for
        """

        # Run a check on the command to make sure the author can run it
        try:
            await command.can_run(self.context)
        
            # Create an embed to show the command and the subcommands
            embed = Embed(
                title = command.qualified_name,
                description = command.description,
                colour = await get_embed_color(self.context.author)
            )

            if len(command.aliases) > 0:
                embed.add_field(
                    name = "Aliases",
                    value = ", ".join([
                        f"`{alias}`"
                        for alias in command.aliases
                    ]),
                    inline = False
                )
            
            # Only add parameters if there are any 
            if len(command.clean_params) > 0:
                embed.add_field(
                    name = "Parameters",
                    value = "\n".join([
                        "`{}`".format(parameter)
                        for parameter in command.clean_params
                    ])
                )
        
        # The author can't run it so they can't get help on the command
        except:
            embed = get_error_message("You can't access this command!")

        await self.context.send(embed = embed)