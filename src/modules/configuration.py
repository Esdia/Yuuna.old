from src.utils.perm import allowed


# This function allows the user to change the server-local command prefix
async def prefix(infos):
    msg = infos.message.content.split()

    # There, the user wants to see the current prefix
    if len(msg) == 1:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["config.prefix.get"].format(infos.prefix)
        )

    # The user should not be mentioning anything
    elif infos.message.mentions or infos.message.channel_mentions or infos.message.role_mentions:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["infos.error.syntax"]
        )

    else:
        if not allowed(infos, "manage_server"):
            await infos.storage.set(
                "prefix",
                msg[1]
            )
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["config.prefix.set"].format(
                    msg[1]
                )
            )
        else:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["infos.error.permission.author.missing"]
            )


# This function allows the user to change the server-local language
async def language(infos):
    msg = infos.message.content.split()

    if not allowed(infos, "manage_server"):
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.permission.author.missing"]
        )

    else:
        if len(msg) != 2 or infos.message.mentions or infos.message.channel_mentions or infos.message.role_mentions:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["info.error.syntax"]
            )
        else:
            if msg[1] not in ["en", "fr"]:
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["config.language.not_found"]
                )
            else:
                await infos.storage.set(
                    "language",
                    msg[1]
                )
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["config.language.set"].format(
                        infos.text_data[
                            "language.{}".format(msg[1])
                        ]
                    )
                )
