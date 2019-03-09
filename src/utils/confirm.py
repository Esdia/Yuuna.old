async def confirm(infos):
    message = await infos.client.send_message(
        infos.message.channel,
        infos.text_data["utils.confirm"]
    )
    reactions = [
        "✅",
        "❌"
    ]
    for r in reactions:
        await infos.client.add_reaction(
            message,
            r
        )

    res = await infos.client.wait_for_reaction(
        reactions,
        user=infos.message.author,
        message=message,
        timeout=120
    )

    if res is None:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["utils.confirm.inactivity"]
        )
        return False
    else:
        await infos.client.delete_message(
            message
        )
        return res.reaction.emoji == "✅"

