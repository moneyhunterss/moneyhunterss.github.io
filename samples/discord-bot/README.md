# Discord Bot — Slash Commands + Role Management

Production-ready Discord bot skeleton. Built on discord.py 2.x with slash
commands, role-based permissions, and clean error handling.

## Features

- Slash commands (`/ping`, `/echo`, `/userinfo`, `/purge`, `/role`)
- Member join welcome message
- Self-role assignment (`/role <name>` to add/remove)
- Role-based permissions (`/purge` requires `manage_messages`)
- Embeds with thumbnails (rich message formatting)
- Graceful error handling (missing perms, command not found)
- Latency reporting

## Quick start

```bash
pip install discord.py

# Get a bot token: https://discord.com/developers/applications
# Create app → Bot → Copy token

# Run the bot
export DISCORD_TOKEN="your-bot-token-here"
python bot.py
```

Invite the bot to your server with the following permissions:
- `applications.commands` (slash commands)
- `bot` scope
- Permissions: `Send Messages`, `Manage Messages`, `Manage Roles`, `Read Message History`

## Slash commands

| Command | Args | Permission | Description |
|---------|------|------------|-------------|
| `/ping` | — | everyone | Check bot latency |
| `/echo <message>` | message | everyone | Echo back (ephemeral) |
| `/userinfo [user]` | user (optional) | everyone | Show user info embed |
| `/purge <count>` | 1-100 | Manage Messages | Bulk delete messages |
| `/role <name>` | role name | everyone | Self-assign role |

## Event handlers

- `on_ready` — sync slash commands, log bot start
- `on_member_join` — welcome new members
- `on_message` — process commands (bots don't trigger this for own messages)
- `on_command_error` — graceful error handling (missing perms, command not found)

## Production upgrades (for paying clients)

- Database integration (Postgres via `asyncpg`, Redis for caching)
- Modular cogs (split commands into separate files for maintainability)
- Scheduled tasks (`discord.ext.tasks` for cron-style jobs)
- Webhook integration (GitHub commits → channel)
- Moderation log channel
- Anti-spam rate limiting
- Welcome message customization via DB

## Tech

- Python 3.10+
- `discord.py` 2.x — async Discord API wrapper
- `app_commands` — slash command framework
- `discord.Intents` — privileged intents (members + message_content)

## License

MIT — for building Discord bots for your own communities.
