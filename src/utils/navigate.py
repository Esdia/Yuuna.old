"""
    This module manages the navigation in an embed with more than one page
"""


# This function is used to edit an embed message
async def update_message(client, message, embed):
    await client.edit_message(
        message,
        embed=embed
    )


async def navigate(client, message, author, list_pages):
    # i is the index of the page we are viewing, in a the list of pages
    i = 0
    maxi = len(list_pages)
    reactions = ['⬅', '➡']

    for r in reactions:
        await client.add_reaction(message, r)

    # After the 1 minute delay, the bot stops the navigation
    res = await client.wait_for_reaction(
        reactions,
        message=message,
        user=author,
        timeout=60
    )

    while res is not None:
        react = res.reaction.emoji
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
        if message.server.me.server_permissions.manage_messages:
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
            reactions,
            message=message,
            user=author,
            timeout=60
        )

    if message.server.me.server_permissions.manage_messages:
        await client.clear_reactions(
            message
        )
