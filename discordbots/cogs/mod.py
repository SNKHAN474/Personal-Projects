import re
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, Member, Message, SlashOption
from datetime import timedelta
import asyncio
import datetime

class Mod(commands.Cog):

    
    server_id = '' # in `discordbot tokens.txt`

    def __init__(self, client):
        self.client = client
        self.softblacklist_words = ["paki", "slur1"]
        self.hardblacklist_words = ["nigg"]

    def is_blacklisted(self, message_content):
        # If any of the hardblacklist words show up in the sender's message returns hard
        for word in self.hardblacklist_words:
            if re.search(rf'{re.escape(word)}', message_content, re.IGNORECASE):
                return "hard"

        # If only the entire soft word show up in the sender's message returns hard
        for word in self.softblacklist_words:
            if re.search(rf'\b{re.escape(word)}\b', message_content, re.IGNORECASE):
                return "soft"

        return None

    async def check_and_handle_permissions(
        self, 
        context, 
        action_type, 
        target_member=None, 
        permission_check_func=None, 
        action_func=None, 
        reason=None
    ):
        """
        Centralized method to handle permission checks and error handling
        
        :param context: Interaction or Message object
        :param action_type: Type of action (e.g., 'mute', 'kick', 'ban')
        :param target_member: Member to perform action on
        :param permission_check_func: Function to check user's permissions
        :param action_func: Function to perform the actual action
        :param reason: Reason for the action
        :return: Tuple (success, error_message)
        """
        # Determine the context type
        is_interaction = isinstance(context, Interaction)
        
        # Permission and bot capability checks
        if is_interaction:
            # Check user permissions
            if permission_check_func and not permission_check_func(context.user):
                await context.response.send_message(
                    f"You don't have permission to {action_type} members.", 
                    ephemeral=True
                )
                return False, "Insufficient user permissions"

            # Check bot permissions
            bot_permissions = getattr(context.guild.me.guild_permissions, f"{action_type}_members", False)
            if not bot_permissions:
                await context.response.send_message(
                    f"I don't have permission to {action_type} members.", 
                    ephemeral=True
                )
                return False, "Insufficient bot permissions"
        else:
            # For on_message event
            bot_permissions = context.guild.me.guild_permissions.mute_members
            if not bot_permissions:
                await context.channel.send(f"I do not have the permission to {action_type} members.")
                return False, "Insufficient bot permissions"

        # Perform the action
        try:
            if action_func:
                await action_func()
            return True, None
        except nextcord.Forbidden:
            error_msg = f"I cannot {action_type} the member due to insufficient permissions."
            if is_interaction:
                await context.response.send_message(error_msg, ephemeral=True)
            else:
                await context.channel.send(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"An error occurred during {action_type}: {e}"
            if is_interaction:
                await context.response.send_message(error_msg, ephemeral=True)
            else:
                await context.channel.send(error_msg)
            return False, error_msg

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        bot_highest_role = message.guild.me.top_role
        if message.author.top_role.position >= bot_highest_role.position:
            return

        blacklist_result = self.is_blacklisted(message.content)
        if blacklist_result in ["hard", "soft"]:
            await message.channel.send(f"{message.author.mention}, your message contains inappropriate language and has been flagged.")
            
            # Delete the user's message
            try:
                await message.delete()
            except nextcord.Forbidden:
                await message.channel.send("I do not have permission to delete messages.")
            except Exception as e:
                await message.channel.send(f"An error occurred: {e}")
                return

            # Timeout the user
            await self.check_and_handle_permissions(
                context=message,
                action_type='mute',
                target_member=message.author,
                action_func=lambda: message.author.timeout(
                    datetime.timedelta(seconds=600), 
                    reason="Blacklisted word"
                )
            )
    @nextcord.slash_command(name="kick", description="Kicks a member", guild_ids=[server_id])
    async def kick(
    self, 
    interaction: Interaction, 
    member: Member, 
    reason: str = SlashOption(description="Reason for kicking", required=False)):
        # Check role hierarchy
        bot_highest_role = interaction.guild.me.top_role
        if member.top_role.position >= bot_highest_role.position:
            await interaction.response.send_message(
                f"I cannot kick {member.mention} because their highest role is higher than or equal to my highest role.",
                ephemeral=True
            )
            return

        success, _ = await self.check_and_handle_permissions(
            context=interaction,
            action_type='kick',
            target_member=member,
            permission_check_func=lambda user: user.guild_permissions.kick_members,
            action_func=lambda: member.kick(reason=f"Kicked by {interaction.user}: {reason or 'No reason provided'}")
        )

        if success:
            await interaction.response.send_message(
                f"{member.mention} has been kicked. Reason: {reason or 'No reason provided'}.", 
                ephemeral=True
            )
    @nextcord.slash_command(name="ban", description="Bans a specified member", guild_ids=[server_id])
    async def ban(self, interaction: Interaction, member: Member, reason: str = SlashOption(description="Reason for banning", required=False), delete_message_days: int = SlashOption(description="Days of messages to delete", default=0, min_value=0, max_value=7)):
        # Check role hierarchy
        bot_highest_role = interaction.guild.me.top_role
        if member.top_role.position >= bot_highest_role.position:
            await interaction.response.send_message(
                f"I cannot ban {member.mention} because their highest role is higher than or equal to my highest role.",
                ephemeral=True
            )
            return

        success, _ = await self.check_and_handle_permissions(
            context=interaction,
            action_type='ban',
            target_member=member,
            permission_check_func=lambda user: user.guild_permissions.ban_members,
            action_func=lambda: member.ban(
                reason=f"Banned by {interaction.user}: {reason or 'No reason provided'}",
                delete_message_days=delete_message_days
            )
        )

        if success:
            await interaction.response.send_message(
                f"{member.mention} has been banned. Reason: {reason or 'No reason provided'}.", 
                ephemeral=True
            )

    @nextcord.slash_command(name="mute", description="Mutes a specified member", guild_ids=[server_id])
    async def mute(
        self,
        interaction: Interaction,
        member: Member = SlashOption(description="The member to mute"),
        duration: str = SlashOption(description="Duration of the mute (e.g., 10m, 1h, 2d)"),
        reason: str = SlashOption(description="Reason for the mute", required=False)
    ):
        # Parse the duration
        match = re.fullmatch(r"(\d+)([smhd])?", duration.lower())
        if not match:
            await interaction.response.send_message(
                "Invalid duration format. Use a number followed by 's', 'm', 'h', or 'd'. (e.g., 10m, 1h, 2d)", 
                ephemeral=True
            )
            return

        value = int(match.group(1))
        unit = match.group(2) or "m"  # Default to minutes if no unit is provided
        duration_seconds = {"s": value, "m": value * 60, "h": value * 3600, "d": value * 86400}.get(unit)

        # Convert the duration to a timedelta object
        duration_timedelta = datetime.timedelta(seconds=duration_seconds)

        # Check role hierarchy
        bot_highest_role = interaction.guild.me.top_role
        if member.top_role.position >= bot_highest_role.position:
            await interaction.response.send_message(
                f"I cannot mute {member.mention} because their highest role is higher than or equal to my highest role.",
                ephemeral=True
            )
            return

        success, _ = await self.check_and_handle_permissions(
            context=interaction,
            action_type='mute',
            target_member=member,
            permission_check_func=lambda user: user.guild_permissions.mute_members,
            action_func=lambda: member.timeout(
                duration_timedelta, 
                reason=reason or "No reason provided"
            )
        )

        if success:
            await interaction.response.send_message(
                f"{member.mention} has been muted for {value}{unit}. "
                f"Reason: {reason or 'No reason provided'}.",
                ephemeral=True
            )

    @nextcord.slash_command(name="test", description="test", guild_ids=[server_id])
    async def test(self, interaction: Interaction):
        await interaction.response.send_message("Test works")

def setup(bot):
    bot.add_cog(Mod(bot))
