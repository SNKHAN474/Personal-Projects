import nextcord
from nextcord.ext import commands
from nextcord import application_command
from nextcord import Interaction
from nextcord import Member

class Mod(commands.Cog):

    def __init__(self, client):
        self.client = client

    server_id = 'id here'

    @nextcord.slash_command(name="test", description="test", guild_ids=[server_id])
    async def test(self, interaction: Interaction):
        await interaction.response.send_message("Test works I guess?")

    
    @nextcord.slash_command(name="kick", description="Kicks a specified member", guild_ids=[server_id])
    async def kick(self, interaction: Interaction, member: Member, reason: str = None):
        # Check if the user has the perms to kick a member
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("You don't have the permissions to use this command.")
            return

        # Check if the bot has perms to kick a member
        if not interaction.guild.me.guild_permissions.kick_members:
            await interaction.response.send_message("I don't have permission to kick members.")
            return

        # Default reason if none is provided
        if reason is None:
            reason = "No reason provided"

        # Attempt to kick the member
        try:
            await member.kick(reason=f"Kicked by {interaction.user}: {reason}")
            await interaction.response.send_message(f"{member.mention} has been kicked by {interaction.user}. Reason: {reason}", empheral=True)
        except nextcord.Forbidden:
            await interaction.response.send_message(f"I cannot kick {member.mention} due to insufficient permissions.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}")

    @nextcord.slash_command(name="ban", description="Bans a specified member", guild_ids=[server_id])
    async def kick(self, interaction: Interaction, member: Member, reason: str = None):
        # Check if the user has the perms to ban a member
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("You don't have the permissions to use this command.")
            return

        # Check if the bot has perms to ban a member
        if not interaction.guild.me.guild_permissions.kick_members:
            await interaction.response.send_message("I don't have permission to ban members.")
            return

        # Default reason if none is provided
        if reason is None:
            reason = "No reason provided"

        # Attempt to ban the member
        try:
            await member.ban(reason=f"Banned by {interaction.user}: {reason}")
            await interaction.response.send_message(f"{member.mention} has been banned by {interaction.user}. Reason: {reason}",empheral=True)
        except nextcord.Forbidden:
            await interaction.response.send_message(f"I cannot ban {member.mention} due to insufficient permissions.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}")


def setup(bot):
    bot.add_cog(Mod(bot))
