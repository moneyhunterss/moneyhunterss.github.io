#!/usr/bin/env python3
"""Discord bot skeleton — slash commands + event handlers.

Production-ready Discord bot with slash commands, role-based permissions,
and a clean command registry. Built on discord.py 2.x.

Usage:
    export DISCORD_TOKEN="your-bot-token"
    python bot.py
"""
from __future__ import annotations
import os
import logging
import sys
from typing import Optional

try:
    import discord
    from discord import app_commands
    from discord.ext import commands
except ImportError:
    print("Install: pip install discord.py", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bot")

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready():
    """Called when bot is connected to Discord."""
    log.info(f"Logged in as {bot.user} (id: {bot.user.id})")
    # Sync slash commands to Discord (guild-specific for instant update,
    # global for ~1h propagation)
    try:
        synced = await bot.tree.sync()
        log.info(f"Synced {len(synced)} slash commands")
    except Exception as e:
        log.error(f"Failed to sync commands: {e}")


@bot.event
async def on_member_join(member: discord.Member):
    """Welcome new members."""
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome {member.mention}! Type `/help` to get started.")


@bot.event
async def on_message(message: discord.Message):
    """Handle messages. Bots don't trigger this for their own messages."""
    if message.author == bot.user:
        return
    # Process commands
    await bot.process_commands(message)


# ─── Slash commands ───────────────────────────────────────────

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Health check."""
    latency_ms = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! {latency_ms}ms")


@bot.tree.command(name="echo", description="Echo a message back")
@app_commands.describe(message="The message to echo")
async def echo(interaction: discord.Interaction, message: str):
    """Echo command — useful for testing."""
    # ephemeral=True means only the caller sees the response
    await interaction.response.send_message(f"You said: {message}", ephemeral=True)


@bot.tree.command(name="userinfo", description="Get info about a user")
@app_commands.describe(user="The user to inspect (defaults to you)")
async def userinfo(
    interaction: discord.Interaction,
    user: Optional[discord.Member] = None,
):
    """Show user info — demonstrates fetching user data."""
    target = user or interaction.user
    embed = discord.Embed(
        title=f"User info — {target.display_name}",
        color=target.color if isinstance(target, discord.Member) else discord.Color.blue(),
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="ID", value=target.id, inline=True)
    embed.add_field(name="Account created", value=target.created_at.strftime("%Y-%m-%d"), inline=True)
    if isinstance(target, discord.Member):
        embed.add_field(name="Joined server", value=target.joined_at.strftime("%Y-%m-%d") if target.joined_at else "?", inline=True)
        roles = [r.mention for r in target.roles if r.name != "@everyone"]
        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join(roles[:10]) or "None", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="purge", description="Delete N messages (mods only)")
@app_commands.describe(count="Number of messages to delete (1-100)")
@app_commands.default_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, count: int):
    """Bulk delete — demonstrates role-based permissions."""
    if not 1 <= count <= 100:
        await interaction.response.send_message("Count must be 1-100", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=count)
    await interaction.followup.send(f"🗑️ Deleted {len(deleted)} messages", ephemeral=True)


@bot.tree.command(name="role", description="Assign or remove a role from yourself")
@app_commands.describe(role_name="Name of the self-assignable role")
async def role(interaction: discord.Interaction, role_name: str):
    """Self-role assignment — demonstrates role management."""
    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("This command only works in servers.", ephemeral=True)
        return
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if not role:
        await interaction.response.send_message(f"Role '{role_name}' not found.", ephemeral=True)
        return
    if role in interaction.user.roles:
        await interaction.user.remove_roles(role)
        await interaction.response.send_message(f"❌ Removed role {role.mention}", ephemeral=True)
    else:
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"✅ Added role {role.mention}", ephemeral=True)


# ─── Prefix commands (legacy fallback) ────────────────────────

@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    """Show available commands."""
    help_text = (
        "**Commands:**\n"
        "`/ping` — check latency\n"
        "`/echo <message>` — echo back\n"
        "`/userinfo [user]` — show user info\n"
        "`/purge <count>` — bulk delete (mods)\n"
        "`/role <name>` — self-assign role"
    )
    await ctx.send(help_text)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Handle command errors gracefully."""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission for that.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # ignore unknown commands
    else:
        log.error(f"Command error: {error}")
        await ctx.send(f"⚠️ Error: {error}")


def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("Error: set DISCORD_TOKEN env var", file=sys.stderr)
        sys.exit(1)
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()
