# This functions wait for a second player to join the game
async def wait_for_player(infos, message):
    reaction = "🇯"
    await infos.client.add_reaction(
        message,
        reaction
    )

    res = None
    ok = False
    while not ok:
        res = await infos.client.wait_for_reaction(
            reaction,
            message=message,
            timeout=120
        )
        if res is None or (not res.user.bot and res.user != infos.message.author):
            ok = True

    if infos.manage_messages:
        await infos.client.clear_reactions(message)

    if res is None:
        return None
    else:
        return res.user
