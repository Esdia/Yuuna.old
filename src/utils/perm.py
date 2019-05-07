"""
    This module is used to check if a user is allowed to do what they are trying to do:
    either they have the required permission, or they have a bot-master role
"""


async def allowed(infos, perm):
    perm_str = "infos.message.author.server_permissions.{}".format(
        perm
    )
    if eval(perm_str):
        return True

    bot_master_id = await infos.storage.get("bot_master")

    if not bot_master_id:
        return False

    return any(role.id == bot_master_id for role in infos.message.author.roles)
