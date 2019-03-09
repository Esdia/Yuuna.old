from discord import Embed
from discord import utils
from src.utils.navigate import navigate
from src.utils.confirm import confirm

from src.modules.bank import bank_add

from random import randint

"""
    This module manages the ranking system by XP
"""


# returns the needed xp to level up from the specified level
def get_needed_xp(level):
    return 180 * level + 150


# returns the level, given the xp
def get_level(xp):
    level = 0
    needed_xp = get_needed_xp(level)
    while xp >= needed_xp:
        level += 1
        xp -= needed_xp
        needed_xp = get_needed_xp(level)

    return level


# return the remaining xp, given the level
def get_remaining_xp(xp, level):
    for i in range(level):
        xp -= get_needed_xp(i)
    return xp


# returns the rank of the member
async def get_rank(member, storage):
    members = await storage.sort(
        'users:xp',
        by='user:*:xp',
        offset=0,
        count=-1
    )
    # storage.sort returns a list sorted in crescent order, but we want the first member to have the highest xp
    # so we have to reverse the list
    members = list(reversed(members))
    # We add one since python indexes lists from 0
    return members.index(member.id) + 1


async def get_member_info(member, storage):
    members = await storage.smembers("users:xp")
    if member.id not in members:
        return None

    xp = int(
        await storage.get("user:{}:xp".format(member.id))
    )
    level = get_level(xp)
    remaining_xp = get_remaining_xp(xp, level)
    xp_to_next = get_needed_xp(level)
    rank = await get_rank(member, storage)
    total = len(members)

    return {
        "total_xp": xp,
        "level": level,
        "remaining_xp": remaining_xp,
        "needed_xp": xp_to_next,
        "rank": rank,
        "total": total
    }


async def rank_command(infos, members=None):
    members = [infos.message.author] if members is None else members

    for m in members:
        member_info = await get_member_info(m, infos.storage)
        if member_info is None:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["levels.error.not_ranked"].format(
                    m.mention
                )
            )
        else:
            embed = Embed(
                title="",
                description="",
                color=0xD828D0
            )
            embed.set_author(
                name=m.display_name,
                icon_url=m.avatar_url
            )
            embed.add_field(
                name="XP",
                value="{}/{} (total : {})".format(
                    member_info["remaining_xp"],
                    member_info["needed_xp"],
                    member_info["total_xp"]
                ),
                inline=False
            )
            embed.add_field(
                name=infos.text_data["levels.level"],
                value=str(member_info["level"]),
                inline=False
            )
            embed.add_field(
                name=infos.text_data["levels.rank"],
                value="{}/{}".format(
                    member_info["rank"],
                    member_info["total"]
                )
            )
            await infos.client.send_message(
                infos.message.channel,
                embed=embed
            )


# Ban some channels from the ranking system
# At this point, and for the next 3 functions too, we know that
# the author is allowed to do whatever they are trying to
async def ban(infos, channels):
    for c in channels:
        await infos.storage.sadd(
            "levels:banned_channels",
            c.id
        )
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["levels.ban"].format(
                c.mention
            )
        )


# Unban some channels from the levelling system
async def unban(infos, channels):
    for c in channels:
        await infos.storage.srem(
            "levels:banned_channels",
            c.id
        )
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["levels.unban"].format(
                c.mention
            )
        )


async def ban_list(infos):
    channels = await infos.storage.smembers('levels:banned_channels')
    printable = ""

    for channel_id in channels:
        channel = utils.get(
            infos.message.server.channels,
            id=channel_id
        )
        printable += "{}\n".format(
            channel.mention
        )

    if printable == "":
        printable = infos.text_data["levels.no_banned"]

    embed = Embed(
        title=infos.text_data["levels.banned.list"],
        description="",
        color=0xD828D0
    )
    embed.add_field(
        name=infos.text_data["levels.reward.channels"],
        value=printable,
        inline=False
    )

    await infos.client.send_message(
        infos.message.channel,
        embed=embed
    )


async def enable(infos):
    await infos.storage.set(
        "level_enabled",
        1
    )
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["levels.enable"]
    )


async def disable(infos):
    await infos.storage.delete(
        "level_enabled"
    )
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["levels.disable"]
    )


async def reset(infos, members):
    for m in members:
        await infos.storage.delete(
            "user:{}:xp".format(
                m.id
            )
        )
        await infos.storage.srem(
            "users:xp",
            m.id
        )
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["levels.done"]
    )


# Called when we have a command that starts exactly by "y!rank". ranktop is not included
async def interpret(infos):
    msg = infos.message.content.split()
    if len(msg) > 1:
        if msg[1] in ["ban", "unban", "0", "1", "reset"]:
            if not infos.message.author.server_permissions.manage_messages:
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["info.error.permission.author.missing"]
                )
            else:
                if msg[1] in ["ban", "unban"]:
                    channels = infos.message.channel_mentions
                    if not channels:
                        if msg[1] == "ban":
                            await ban_list(infos)
                        else:
                            await infos.client.send_message(
                                infos.message.channel,
                                infos.text_data["info.error.syntax"]
                            )
                    elif msg[1] == "ban":
                        await ban(infos, channels)
                    else:
                        await unban(infos, channels)
                elif msg[1] == "reset":
                    if await confirm(infos):
                        members = infos.message.mentions
                        members = infos.message.server.members if not members else members
                        await reset(infos, members)
                else:
                    if msg[1] == "1":
                        await enable(infos)
                    else:
                        await disable(infos)
        else:
            mentions = infos.message.mentions
            if not mentions:
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["info.error.syntax"]
                )
            else:
                await rank_command(infos, mentions)
    else:
        await rank_command(infos)


async def ranktop(infos):
    members = await infos.storage.sort(
        'users:xp',
        by='user:*:xp',
        offset=0,
        count=-1
    )

    # storage.sort returns a list sorted in crescent order, but we want the first member to have the highest xp
    # so we have to reverse the list
    members = list(reversed(members))
    list_pages = []

    embed = Embed(
        title=infos.text_data["levels.ranktop"],
        description="",
        color=0xD828D0
    )

    i = 0
    for i in range(len(members)):
        member = utils.get(
            infos.message.server.members,
            id=members[i]
        )
        member_infos = await get_member_info(
            member,
            infos.storage
        )

        embed.add_field(
            name="{}. {}".format(
                i+1,
                member.display_name
            ),
            value="{} : {} | {} / {} XP (total : {} XP)".format(
                infos.text_data["levels.level"],
                member_infos["level"],
                member_infos["remaining_xp"],
                member_infos["needed_xp"],
                member_infos["total_xp"]
            ),
            inline=False
        )

        if (i + 1) % 10 == 0:     # Proc once every ten members
            list_pages.append(embed)
            embed = Embed(
                title=infos.text_data["levels.ranktop"],
                description="",
                color=0xD828D0
            )

    if (i + 1) % 10 != 0:
        list_pages.append(embed)

    for i in range(len(list_pages)):
        list_pages[i].set_footer(
            text=infos.text_data["embed.footer"].format(
                i+1,
                len(list_pages)
            )
        )

    message = await infos.client.send_message(
        infos.message.channel,
        embed=list_pages[0]
    )

    if len(list_pages) > 1:
        await navigate(
            infos.client,
            message,
            infos.message.author,
            list_pages
        )


async def get_rewards(infos):
    rewards = await infos.storage.smembers('levels:rewards')
    if rewards is None:
        rewards = []
    printable = ""

    for level in rewards:
        role_id = await infos.storage.get(
            "levels:reward:{}".format(
                level
            )
        )
        role = utils.get(
            infos.message.server.roles,
            id=role_id
        )
        if role is not None:
            printable += "{} {} : {}\n".format(
                infos.text_data["levels.level"],
                level,
                role.mention
            )

    if printable == "":
        printable = infos.text_data["levels.no_rewards"]

    embed = Embed(
        title=infos.text_data["levels.reward.list"],
        description="",
        color=0xD828D0
    )
    embed.add_field(
        name=infos.text_data["levels.reward.roles"],
        value=printable,
        inline=False
    )

    await infos.client.send_message(
        infos.message.channel,
        embed=embed
    )


async def set_reward(infos, role, level):
    await infos.storage.sadd(
        "levels:rewards",
        level
    )
    await infos.storage.set(
        "levels:reward:{}".format(
            level
        ),
        role.id
    )
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["levels.reward.set"].format(
            role.mention,
            level
        )
    )


async def del_reward(infos, level):
    await infos.storage.srem(
        "levels:rewards",
        level
    )
    await infos.storage.delete(
        "levels:reward:{}".format(
            level
        )
    )
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["levels.reward.del"].format(
            level
        )
    )


async def rewards_interpret(infos):
    msg = infos.message.content.split()

    if not infos.message.author.server_permissions.manage_server:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.permission.author.missing"]
        )
    elif len(msg) == 1:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
    else:
        if msg[1] == "list":
            await get_rewards(infos)
            return
        elif msg[1] in ["set", "delete"]:
            n_str = [
                s for s in msg if s.isdigit()
            ]
            if n_str:
                n = int(
                    n_str[0]
                )
                if msg[1] == "set":
                    mentions = infos.message.role_mentions
                    if mentions:
                        role = mentions[0]
                        await set_reward(infos, role, n)
                        return
                    else:
                        pass
                else:
                    await del_reward(infos, n)
                    return
            else:
                pass
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )


# Called when someone speaks, to give them xp
async def give_xp(infos):
    author = infos.message.author

    is_enabled = await infos.storage.get(
        "level_enabled"
    )
    banned_channels = list(
        await infos.storage.smembers(
            "levels:banned_channels"
        )
    )

    if (not is_enabled) or (infos.message.channel.id in banned_channels):
        return

    # We add the member in the database
    # sadd only add if the element is not already in the list, so no risk of doubles
    await infos.storage.sadd(
        "users:xp",
        author.id
    )

    anti_spam = await infos.storage.get(
        "user:{}:anti_spam".format(
            author.id
        )
    )
    # It means that they sent a message less than one minute ago
    if anti_spam:
        return

    xp = await infos.storage.get(
        "user:{}:xp".format(
            author.id
        )
    )

    xp = 0 if xp is None else int(xp)

    level = get_level(xp)

    given_xp = randint(10, 20)

    await infos.storage.set(
        "user:{}:xp".format(
            author.id
        ),
        xp + given_xp
    )

    new_level = get_level(xp + given_xp)

    await infos.storage.set(
        "user:{}:anti_spam".format(
            author.id
        ),
        1,
        expire=60
    )

    if level != new_level:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["levels.level_up"].format(
                author.mention,
                new_level
            )
        )

        reward_id = await infos.storage.get(
            "levels:reward:{}".format(
                new_level
            )
        )

        # Whe you level up, you earn 50 coins
        await bank_add(
            infos,
            author,
            50,
            level_up=True
        )

        if reward_id is not None:
            reward = utils.get(
                infos.message.server.roles,
                id=reward_id
            )
            await infos.client.add_roles(
                author,
                reward
            )
