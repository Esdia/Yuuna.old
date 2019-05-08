from discord import Embed
from discord import utils

from src.utils.navigate import navigate
from src.utils.confirm import confirm
from src.utils.perm import allowed


async def get_coins(storage, member):
    coins = await storage.get(
        "user:{}:bank".format(
            member.id
        )
    )
    coins = 0 if coins is None else int(coins)
    return coins


async def bank_add(infos, member, n, level_up=False):
    users = await infos.storage.smembers("users:bank")
    if member.id not in users:
        await infos.storage.sadd(
            "users:bank",
            member.id
        )
        await infos.storage.set(
            "user:{}:bank".format(
                member.id
            ),
            n
        )
    else:
        await infos.storage.incrby(
            "user:{}:bank".format(
                member.id
            ),
            n
        )

    if not level_up:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["bank.add"].format(
                member.mention,
                n
            )
        )


async def bank_remove(infos, member, n, shop=False):
    await infos.storage.sadd(
        "users:bank",
        member.id
    )
    coins = await get_coins(infos.storage, member)

    # If you have like 15 coins, and you are removed 20, you did not lose 20 coins, but 15
    # new_coins is there to keep that in memory, for an accurate message sent after the operation
    new_coins = coins - n if coins >= n else 0
    if new_coins == 0:
        await infos.storage.delete(
            "user:{}:bank".format(
                member.id
            )
        )
        await infos.storage.srem(
            "users:bank",
            member.id
        )
    else:
        await infos.storage.set(
            "user:{}:bank".format(
                member.id
            ),
            new_coins
        )

    if not shop:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["bank.remove"].format(
                member.mention,
                coins - new_coins
            )
        )


async def bank_set(infos, member, n):
    if n != 0:
        await infos.storage.sadd(
            "users:bank",
            member.id
        )
        await infos.storage.set(
            "user:{}:bank".format(
                member.id
            ),
            n
        )
    else:
        await infos.storage.srem(
            "users:bank",
            member.id
        )
        await infos.storage.delete(
            "user:{}:bank".format(
                member.id
            )
        )
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["bank.set"].format(
            member.mention,
            n
        )
    )


async def bank_give(infos, members, n):
    coins = await get_coins(infos.storage, infos.message.author)

    if coins < n*len(members):
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["bank.not_enough_coins"]
        )
    else:
        await bank_remove(
            infos,
            infos.message.author,
            n*len(members)
        )
        for m in members:
            await bank_add(
                infos,
                m,
                n
            )


async def get_rank(storage, member):
    members = await storage.sort(
        'users:bank',
        by='user:*:bank',
        offset=0,
        count=-1
    )
    # storage.sort returns a list sorted in crescent order, but we want the first member to have the highest xp
    # so we have to reverse the list
    members = list(reversed(members))
    # We add one since python indexes lists from 0
    if member.id in members:
        return (
            members.index(member.id) + 1,
            len(members)
        )
    else:
        return None


async def bank(infos, members=None):
    members = [infos.message.author] if members is None else members

    for m in members:
        coins = await get_coins(infos.storage, m)
        rank = await get_rank(infos.storage, m)

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
            name=infos.text_data["bank.coins"],
            value="{}".format(coins),
            inline=True
        )
        if rank is not None:
            embed.add_field(
                name=infos.text_data["bank.rank"],
                value="{}/{}".format(
                    rank[0],
                    rank[1]
                ),
                inline=True
            )
        await infos.client.send_message(
            infos.message.channel,
            embed=embed
        )


async def banktop(infos):
    members = await infos.storage.sort(
        'users:bank',
        by='user:*:bank',
        offset=0,
        count=-1
    )

    # storage.sort returns a list sorted in crescent order, but we want the first member to have the highest xp
    # so we have to reverse the list
    members = list(reversed(members))
    list_pages = []

    embed = Embed(
        title=infos.text_data["bank.banktop"],
        description="",
        color=0xD828D0
    )

    i = 0
    for i in range(len(members)):
        member = utils.get(
            infos.message.server.members,
            id=members[i]
        )

        coins = await get_coins(infos.storage, member)

        embed.add_field(
            name="{}. {}".format(
                i+1,
                member.display_name
            ),
            value="{} : {}".format(
                infos.text_data["bank.coins"],
                coins
            ),
            inline=False
        )

        if (i + 1) % 10 == 0:     # Proc once every ten members
            list_pages.append(embed)
            embed = Embed(
                title=infos.text_data["bank.banktop"],
                description="",
                color=0xD828D0
            )

    if (i + 1) % 10 != 0:
        list_pages.append(embed)

    for i in range(len(list_pages)):
        list_pages[i].set_footer(
            text=infos.text_data["embed.footer"].format(
                i + 1,
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


async def interpret(infos):
    msg = infos.message.content.split()
    if len(msg) > 1:
        if msg[1] in ["add", "remove", "set"]:
            if not await allowed(infos, "manage_message"):
                return

            numbers = [i for i in msg if i.isdigit()]
            members = infos.message.mentions
            if not (numbers and members):
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["info.error.syntax"]
                )
            else:
                n = int(numbers[0])
                n = -n if n < 0 else n
                if await confirm(infos):
                    if msg[1] == "add":
                        for m in members:
                            await bank_add(
                                infos,
                                m,
                                n
                            )
                    elif msg[1] == "remove":
                        for m in members:
                            await bank_remove(
                                infos,
                                m,
                                n
                            )
                    else:
                        for m in members:
                            await bank_set(
                                infos,
                                m,
                                n
                            )
        elif msg[1] == "pay":
            numbers = [int(i) for i in msg if i.isdigit()]
            members = infos.message.mentions
            if not (numbers and members):
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["info.error.syntax"]
                )
            elif await confirm(infos):
                n = numbers[0]
                n = -n if n < 0 else n
                await bank_give(
                    infos,
                    members,
                    n
                )
        else:
            members = infos.message.mentions
            if not members:
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["info.error.syntax"]
                )
            else:
                await bank(
                    infos,
                    members
                )
    else:
        await bank(infos)
