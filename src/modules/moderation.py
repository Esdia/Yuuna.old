import discord
from src.utils.confirm import confirm


# perm is true if the user is allowed to do what they're trying to do
# bot_perm is true if the bot is allowed to do what the user is trying to do
async def parse_perms(infos, perm, bot_perm, target=None, mute_command=False):
    if target is not None and target == infos.message.server.owner:
        return infos.text_data["info.error.permission.owner"]
    if not perm:
        return infos.text_data["info.error.permission.author.missing"]
    elif not bot_perm:
        return infos.text_data["info.error.permission.self.missing"]
    else:
        if target is not None and infos.message.author != infos.message.server.owner:
            if target.top_role >= infos.message.author.top_role:
                return infos.text_data["info.error.permission.author.other_higher"]
            elif target.top_role >= infos.message.server.me.top_role and not mute_command:
                return infos.text_data["info.error.permission.self.other_higher"]
    return "OK"


async def purge(infos):
    perm = infos.message.author.server_permissions.manage_messages
    perm_bot = infos.message.server.me.server_permissions.manage_messages
    perm_message = await parse_perms(
        infos,
        perm,
        perm_bot
    )
    if perm_message != "OK":
        await infos.client.send_message(
            infos.message.channel,
            perm_message
        )
    else:
        msg = infos.message.content.split()
        if not msg[1].isdigit():
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["info.error.syntax"]
            )
        elif await confirm(infos):
            n = int(msg[1])
            await infos.client.purge_from(
                infos.message.channel,
                limit=n+1
            )


async def mute(infos):
    members = infos.message.mentions
    if not members:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
    else:
        perm = infos.message.author.server_permissions.manage_messages
        perm_bot = infos.message.server.me.server_permissions.manage_channels

        channels = [c for c in infos.message.server.channels if c.type == discord.ChannelType.text]

        for m in members:
            perm_message = await parse_perms(
                infos,
                perm,
                perm_bot,
                target=m,
                mute_command=True
            )
            if perm_message != "OK":
                await infos.client.send_message(
                    infos.message.channel,
                    perm_message
                )
            elif await confirm(infos):
                for c in channels:
                    overwrite = c.overwrites_for(m)
                    overwrite.send_messages = False
                    await infos.client.edit_channel_permissions(
                        c,
                        m,
                        overwrite
                    )
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["moderation.mute.muted"].format(
                        m.mention
                    )
                )


async def unmute(infos):
    members = infos.message.mentions
    if not members:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
    else:
        perm = infos.message.author.server_permissions.manage_messages
        perm_bot = infos.message.server.me.server_permissions.manage_channels

        channels = [c for c in infos.message.server.channels if c.type == discord.ChannelType.text]

        for m in members:
            perm_message = await parse_perms(
                infos,
                perm,
                perm_bot,
                target=m,
                mute_command=True
            )
            if perm_message != "OK":
                await infos.client.send_message(
                    infos.message.channel,
                    perm_message
                )
            elif await confirm(infos):
                for c in channels:
                    await infos.client.delete_channel_permissions(
                        c,
                        m
                    )
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["moderation.mute.unmuted"].format(
                        m.mention
                    )
                )


async def kick(infos):
    members = infos.message.mentions
    if not members:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
    else:
        perm = infos.message.author.server_permissions.kick_members
        perm_bot = infos.message.server.me.server_permissions.kick_members

        for m in members:
            perm_message = await parse_perms(
                infos,
                perm,
                perm_bot,
                target=m
            )
            if perm_message != "OK":
                await infos.client.send_message(
                    infos.message.channel,
                    perm_message
                )
            elif await confirm(infos):
                await infos.client.kick(m)
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["moderation.kick"].format(
                        m.name
                    )
                )


async def ban(infos):
    members = infos.message.mentions
    if not members:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
    else:
        perm = infos.message.author.server_permissions.ban_members
        perm_bot = infos.message.server.me.server_permissions.ban_members

        for m in members:
            perm_message = await parse_perms(
                infos,
                perm,
                perm_bot,
                target=m
            )
            if perm_message != "OK":
                await infos.client.send_message(
                    infos.message.channel,
                    perm_message
                )
            elif await confirm(infos):
                await infos.client.ban(m)
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["moderation.ban"].format(
                        m.name
                    )
                )
