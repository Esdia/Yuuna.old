from discord import Embed, utils
from src.modules.bank import get_coins, bank_remove

reactions_template = [
    '⬅',
    '➡',
    "0⃣",
    "1⃣",
    "2⃣",
    "3⃣",
    "4⃣",
    "5⃣",
    "6⃣",
    "7⃣",
    "8⃣",
    "9⃣"
]


async def get_price(storage, role):
    price = await storage.get(
        "shop:{}:price".format(
            role.id
        )
    )
    if price is not None:
        return int(price)
    else:
        return None


async def buy(infos, role):
    price = await get_price(
        infos.storage,
        role
    )
    coins = await get_coins(
        infos.storage,
        infos.message.author
    )
    if role in infos.message.author.roles:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["shop.role.already_bought"]
        )
    else:
        if coins >= price:
            await bank_remove(
                infos,
                infos.message.author,
                price,
                shop=True
            )
            await infos.client.add_roles(
                infos.message.author,
                role
            )
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["shop.buy"].format(
                    infos.message.author.mention,
                    role.name
                )
            )
        else:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["bank.not_enough_coins"]
            )


# This function is used to edit an embed message
async def update_message(client, message, embed):
    await client.edit_message(
        message,
        embed=embed
    )


async def navigate_shop(client, message, author, list_pages, reactions, roles):
    # i is the index of the page we are viewing, in a the list of pages
    i = 0
    maxi = len(list_pages)

    print(reactions)

    if maxi == 1:
        # If there is one page, we do not want the arrows to navigate from one page to another
        for react in reactions:
            react.pop(0)
            react.pop(0)

        for r in reactions[0]:
            if r != "":
                await client.add_reaction(
                    message,
                    r
                )
    else:
        for r in reactions_template:
            await client.add_reaction(
                message,
                r
            )

    # After the 1 minute delay, the bot stops the navigation
    res = await client.wait_for_reaction(
        reactions[0],
        message=message,
        user=author,
        timeout=60
    )

    while res is not None:
        react = res.reaction.emoji
        reaction_page = reactions[i]
        if react == '⬅':
            if i > 0:
                i -= 1
            # If we try to go left from the first page, we end up on the last one
            else:
                i = maxi - 1
        elif react == '➡':
            if i < maxi - 1:
                i += 1
            # If we try to go right from the last page, we end up on the first one
            else:
                i = 0
        elif react in reaction_page:
            role_index = reaction_page.index(react) - 2
            # If we have only one page, we cut off the arrows in the reactions
            # So to get the role index, we have to add 2 again
            if maxi == 1:
                role_index += 2
            await client.clear_reactions(message)
            return roles[i][role_index]
        await client.remove_reaction(
            message,
            react,
            author
        )
        await update_message(
            client,
            message,
            list_pages[i]
        )
        res = await client.wait_for_reaction(
            reaction_page,
            message=message,
            user=author,
            timeout=60
        )

    await client.clear_reactions(message)
    return None


async def display_shop(infos):
    roles_id = await infos.storage.sort(
        "shop:roles",
        by="shop:*:price",
        offset=0,
        count=-1
    )

    list_pages = []
    reactions = []
    roles = []

    temp_react = [
        reactions_template[0],
        reactions_template[1]
    ]
    temp_roles = []

    printable = ""

    i = 0
    for _ in range(len(roles_id)):
        role = utils.get(
            infos.message.server.roles,
            id=roles_id[i]
        )

        if role is not None:
            price = await get_price(
                infos.storage,
                role
            )
            temp_react.append(
                reactions_template[
                    i % 10 + 2
                ]
            )
            temp_roles.append(
                role
            )
            printable += "{} {} : {} {}\n".format(
                reactions_template[
                    i % 10 + 2
                ],
                role.mention,
                price,
                infos.text_data["bank.coins"]
            )
            i += 1
        else:
            if role is None:
                await infos.storage.srem(
                    "shop:roles",
                    roles_id[i]
                )
                await infos.storage.delete(
                    "shop:{}:price".format(
                        roles_id[i]
                    )
                )
                roles_id.remove(
                    roles_id[i]
                )

        if i % 10 == 0:  # Proc once every ten members
            embed = Embed(
                title=infos.text_data["shop.shop"],
                description="",
                color=0xD828D0
            )
            embed.add_field(
                name=infos.text_data["shop.roles"],
                value=printable,
                inline=False
            )
            list_pages.append(embed)
            reactions.append(temp_react)
            roles.append(temp_roles)
            temp_react = [
                reactions_template[0],
                reactions_template[1]
            ]
            temp_roles = []
            printable = ""

    # Proc if there are no roles
    # It is done there, after the for, in case of there are roles set in the shop, but which have been deleted
    if len(roles_id) == 0:
        embed = Embed(
            title=infos.text_data["shop.shop"],
            description="",
            color=0xD828D0
        )
        embed.add_field(
            name=infos.text_data["shop.roles"],
            value=infos.text_data["shop.no_roles"],
            inline=False
        )
        await infos.client.send_message(
            infos.message.channel,
            embed=embed
        )
        return

    if i % 10 != 0:
        embed = Embed(
            title=infos.text_data["shop.shop"],
            description="",
            color=0xD828D0
        )
        embed.add_field(
            name=infos.text_data["shop.roles"],
            value=printable,
            inline=False
        )
        roles.append(temp_roles)
        list_pages.append(embed)
        reactions.append(temp_react)

    print(list_pages)
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

    role = await navigate_shop(
        infos.client,
        message,
        infos.message.author,
        list_pages,
        reactions,
        roles
    )
    if role is not None:
        await buy(
            infos,
            role
        )


async def shop_add(infos, role, price):
    await infos.storage.sadd(
        "shop:roles",
        role.id
    )
    await infos.storage.set(
        "shop:{}:price".format(
            role.id
        ),
        price
    )
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["shop.role.added"].format(
            role.mention,
            price
        )
    )


async def shop_remove(infos, role):
    await infos.storage.srem(
        "shop:roles",
        role.id
    )
    await infos.storage.delete(
        "shop:{}:price".format(
            role.id
        )
    )
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["shop.role.removed"].format(
            role.mention,
        )
    )


async def shop_set(infos, role, price):
    former_price = await get_price(
        infos.storage,
        role
    )

    if former_price is None:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["shop.set.error"].format(
                role.mention
            )
        )
    else:
        await infos.storage.set(
            "shop:{}:price".format(
                role.id
            ),
            price
        )
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["shop.set.success"].format(
                role.mention,
                price
            )
        )


async def interpret(infos):
    msg = infos.message.content.split()
    if len(msg) == 1:
        await display_shop(infos)
    else:
        if not infos.message.author.server_permissions.manage_roles:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["info.error.permission.author.missing"]
            )
        elif msg[1] not in ["add", "remove", "set"]:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["info.error.syntax"]
            )
        else:
            roles = infos.message.role_mentions
            if not roles:
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["info.error.syntax"]
                )
            else:
                role = roles[0]
                if msg[1] == "remove":
                    await shop_remove(
                        infos,
                        role
                    )
                else:
                    numbers = [int(i) for i in msg if i.isdigit()]
                    if not numbers:
                        await infos.client.send_message(
                            infos.message.channel,
                            infos.text_data["info.error.syntax"]
                        )
                    else:
                        n = numbers[0]
                        if msg[1] == "add":
                            if role >= infos.message.author.top_role:
                                await infos.client.send_message(
                                    infos.message.channel,
                                    infos.text_data["shop.role_higher"]
                                )
                            else:
                                await shop_add(
                                    infos,
                                    role,
                                    n
                                )
                        else:
                            await shop_set(
                                infos,
                                role,
                                n
                            )
