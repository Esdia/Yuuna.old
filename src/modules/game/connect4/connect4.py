from src.modules.game.connect4.classes import Chip, init

channel_list = []

"""
    This module manages a game of connect4
"""


# Used to update the grid's embed
async def update_embed(infos, game_infos, inactivity=False, tie=False):
    embed = game_infos.embed
    embed.clear_fields()
    embed.set_footer(text="")
    if inactivity:
        head = infos.text_data["game.connect4.inactivity.cancel"]
        value = infos.text_data["game.winner"].format(member=game_infos.winner.mention)
    elif game_infos.winner is not None:
        head = infos.text_data["game.winner"].format(member=" ")
        value = game_infos.winner.mention
    elif tie:
        head = infos.text_data["game.tie"]
        value = ":("
    else:
        head = infos.text_data["game.player.turn"].format(member=" ")
        value = game_infos.turn.mention
    embed.add_field(
        name=head,
        value=value,
        inline=False
    )
    embed.add_field(
        name=infos.text_data["game.connect4.colors"],
        value="{} : {}\n{} : {}".format(
            game_infos.players[0].mention,
            "🔴",
            game_infos.players[1].mention,
            "🔵"
        )
    )
    embed.add_field(
        name=infos.text_data["game.connect4.grid"],
        value=game_infos.create_printable(),
        inline=False
    )
    game_infos.embed = embed
    await infos.client.edit_message(
        game_infos.message,
        embed=game_infos.embed
    )


# Called to end the game
async def end(infos, game_infos, inactivity=False, tie=False):
    await update_embed(
        infos,
        game_infos,
        inactivity=inactivity,
        tie=tie
    )
    if infos.manage_messages:
        await infos.client.clear_reactions(game_infos.message)


# Given a turn (i.e. a player, a color), and the column in which the player wants to play, this functions execute the play
# If the column is full after this turn, the function returns True, so that it is not playable after
def play(game_infos, turn, column):
    grid = game_infos.grid
    colors = [
        "red",
        "blue"
    ]
    i = 0
    # Stating from the bottom, we want to know where to put the chip (on top of all the previous ones)
    while i < 6 and grid[i][column].color != "black":
        i += 1

    grid[i][column] = Chip(
        colors[turn]
    )
    game_infos.grid = grid
    return i == 6


# Manages a game
async def game(infos, game_infos):
    for i in range(49):     # At most there are 7*7 = 49 turns
        turn = i % 2    # 0: player 1, 1: player 2

        await update_embed(
            infos,
            game_infos
        )

        # We only add the reactions on the first turn
        # We do it here, in the while, in order to do it after editing the embed
        if i == 0:
            for r in game_infos.reactions:
                await infos.client.add_reaction(
                    game_infos.message,
                    r
                )

        res = await infos.client.wait_for_reaction(
            game_infos.reactions,
            user=game_infos.players[turn],
            message=game_infos.message,
            timeout=120
        )
        if res is None:
            game_infos.winner = game_infos.players[
                1 - turn
            ]
            await end(
                infos,
                game_infos,
                inactivity=True,
            )
            return
        else:
            react = res.reaction.emoji
            column = game_infos.reactions.index(
                react
            )
            column_full = play(
                game_infos,
                turn,
                column
            )
            if infos.manage_messages:
                await infos.client.remove_reaction(
                    game_infos.message,
                    react,
                    res.user
                )
            if column_full:
                users = await infos.client.get_reaction_users(
                    res.reaction,
                    limit=50
                )
                if infos.manage_messages:
                    for u in users:
                        await infos.client.remove_reaction(
                            game_infos.message,
                            react,
                            u
                        )
                game_infos.reactions[column] = ""

            game_infos.turn = game_infos.players[
                1 - turn
            ]
            game_infos.winner = game_infos.win()
            if game_infos.winner is not None:
                await end(
                    infos,
                    game_infos
                )
                return
    await end(
        infos,
        game_infos,
        tie=True
    )


# Called when someone use the "y!connect4" command, this function starts a game of connect4
async def start(infos):
    channel = infos.message.channel
    if channel.id not in channel_list:
        channel_list.append(channel.id)
        game_infos = await init(infos)

        if game_infos is None:
            await infos.client.send_message(
                channel,
                infos.text_data["game.connect4.inactivity.cancel"]
            )
        else:
            await game(infos, game_infos)
    else:
        infos.client.send_message(
            channel,
            infos.text_data["game.connect4.already_launched"]
        )

    channel_list.remove(channel.id)
