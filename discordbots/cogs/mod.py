import re
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, Member, Message

class Mod(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.softblacklist_words = ["paki", "slur1"]
        self.hardblacklist_words = ["nigg"]

    def is_blacklisted(self, message_content):
        for word in self.hardblacklist_words:
            if re.search(rf'{re.escape(word)}', message_content, re.IGNORECASE):
                return "hard"

        for word in self.softblacklist_words:
            if re.search(rf'\b{re.escape(word)}\b', message_content, re.IGNORECASE):
                return "soft"

        return None

    server_id = ''  # In `discordbot token.txt`

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        
        sender = message.author

        # Checks if the sender has said anything that's been blacklisted
        if self.is_blacklisted(message.content) == "hard" or self.is_blacklisted(message.content) == "soft":
            await message.channel.send(f"{message.author.mention}, your message contains inappropriate language and has been flagged.")
            try:
                await message.delete()
            except nextcord.Forbidden:
                await message.channel.send("I do not have permission to delete messages.")
            except Exception as e:
                await message.channel.send(f"An error occurred: {e}")
        
        

    @nextcord.slash_command(name="test", description="Test command", guild_ids=[server_id])
    async def test(self, interaction: Interaction):
        await interaction.response.send_message("Test works I guess?")

    @nextcord.slash_command(name="kick", description="Kicks a specified member", guild_ids=[server_id])
    async def kick(self, interaction: Interaction, member: Member, reason: str = None):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.kick_members:
            await interaction.response.send_message("I don't have permission to kick members.", ephemeral=True)
            return

        reason = reason or "No reason provided"
        try:
            await member.kick(reason=f"Kicked by {interaction.user}: {reason}")
            await interaction.response.send_message(f"{member.mention} has been kicked by {interaction.user}. Reason: {reason}", ephemeral=True)
        except nextcord.Forbidden:
            await interaction.response.send_message(f"I cannot kick {member.mention} due to insufficient permissions.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

    @nextcord.slash_command(name="ban", description="Bans a specified member", guild_ids=[server_id])
    async def ban(self, interaction: Interaction, member: Member, reason: str = None):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message("I don't have permission to ban members.", ephemeral=True)
            return

        reason = reason or "No reason provided"
        try:
            await member.ban(reason=f"Banned by {interaction.user}: {reason}")
            await interaction.response.send_message(f"{member.mention} has been banned by {interaction.user}. Reason: {reason}", ephemeral=True)
        except nextcord.Forbidden:
            await interaction.response.send_message(f"I cannot ban {member.mention} due to insufficient permissions.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)


def setup(bot):
    bot.add_cog(Mod(bot))
