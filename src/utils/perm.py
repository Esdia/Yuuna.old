"""
    This module is used to check if a user is allowed to do what they are trying to do:
    either they have the required permission, or they have a bot-master role
"""


async def allowed(infos, perm):
    perm_str = "infos.message.author.server_permissions.{}".format(
        perm
    )
    # The perm evaluates to True -> they have the permission
    if eval(perm_str):
        return True

    # There is a bot master role and the user have it -> they are allowed
    bot_master_id = await infos.storage.get("bot_master")
    if bot_master_id and any(role.id == bot_master_id for role in infos.message.author.roles):
        return True

    # There, they are not allowed
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["info.error.permission.author.missing"]
    )
    return False
