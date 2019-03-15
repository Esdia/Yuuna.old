from src.utils.game import wait_for_player
from discord import Embed

player_dict = {}

"""
    This module manages a game of Tic Tac Toe
"""


def get_printable(cases):
    result = cases['↖'] + cases['⬆'] + cases['↗'] + "\n" + \
             cases['⬅'] + cases['⏺'] + cases['➡'] + "\n" + \
             cases['↙'] + cases['⬇'] + cases['↘']
    return result


async def update_print(infos, message, cases):
    await infos.client.edit_message(
        message,
        new_content=get_printable(cases)
    )


def win(cases):
    list_cases = [
        cases['↖'], cases['⬆'], cases['↗'],
        cases['⬅'], cases['⏺'], cases['➡'],
        cases['↙'], cases['⬇'], cases['↘']
    ]
    for i in range(3):
        if list_cases[i] == list_cases[i + 3] == list_cases[i + 6] != '⬜':
            return list_cases[i]

    for i in range(0, 8, 3):
        if list_cases[i] == list_cases[i + 1] == list_cases[i + 2] != '⬜':
            return list_cases[i]

    if list_cases[0] == list_cases[4] == list_cases[8] != '⬜':
        return list_cases[0]

    elif list_cases[2] == list_cases[4] == list_cases[6] != '⬜':
        return list_cases[2]

    return 'N'


async def end(infos, winner, message, inactivity=None):
    players = player_dict[infos.message.channel.id]
    if winner == 'N':
        result = infos.text_data["game.tie"]
    elif winner == '❌':
        result = infos.text_data["game.winner"].format(players[0].mention)
    else:
        result = infos.text_data["game.winner"].format(players[1].mention)
    if inactivity is not None:
        result = "{} {}".format(
            inactivity,
            result
        )
    if infos.manage_messages:
        await infos.client.clear_reactions(message)
    await infos.client.edit_message(
        message,
        new_content=result
    )
    del player_dict[infos.message.channel.id]


async def game(infos, message_cases, message_turn, players, cases, reactions):
    for i in range(9):
        turn = i % 2  # 0: player 1, 1: player 2

        symbol = '❌'
        if turn == 1:
            symbol = "⭕"

        res = await infos.client.wait_for_reaction(
            reactions,
            message=message_turn,
            user=players[turn],
            timeout=120
        )
        if res is None:
            winner = "⭕"
            if turn == 1:
                winner = '❌'
            await end(
                infos,
                winner,
                message_turn,
                inactivity=infos.text_data["game.tic-tac-toe.inactivity.cancel"]
            )
            return

        react = res.reaction.emoji
        cases[react] = symbol
        reactions.remove(react)

        await update_print(
            infos,
            message_cases,
            cases
        )
        if len(reactions) == 0 or not win(cases) == 'N':
            await end(
                infos,
                win(cases),
                message_turn
            )
            return
        else:
            await infos.client.edit_message(
                message_turn,
                new_content=infos.text_data["game.player.turn"].format(
                    players[
                        1 - turn
                    ].mention
                )
            )
            users = await infos.client.get_reaction_users(
                res.reaction,
                limit=50
            )
            if infos.manage_messages:
                for u in users:
                    await infos.client.remove_reaction(
                        message_turn,
                        react,
                        u
                    )


async def start(infos):
    cases = {'↖': '⬜', '⬆': '⬜', '↗': '⬜', '⬅': '⬜', '⏺': '⬜', '➡': '⬜', '↙': '⬜', '⬇': '⬜', '↘': '⬜'}
    reactions = ['↖', '⬆', '↗', '⬅', '⏺', '➡', '↙', '⬇', '↘']
    players = player_dict[infos.message.channel.id]

    print_cases = get_printable(cases)
    print_turn = infos.text_data["game.player.turn"].format(players[0].mention)

    message_case = await infos.client.send_message(
        infos.message.channel,
        print_cases
    )
    message_turn = await infos.client.send_message(
        infos.message.channel,
        print_turn
    )

    for r in reactions:
        await infos.client.add_reaction(
            message_turn,
            r
        )
    await game(
        infos,
        message_case,
        message_turn,
        players,
        cases,
        reactions
    )


async def entry(infos):
    channel_id = infos.message.channel.id
    author = infos.message.author

    if channel_id not in player_dict:
        player_dict[channel_id] = [author]

        embed = Embed(title=infos.text_data["game.tic-tac-toe.name"],
                      description="",
                      color=0xD828D0)
        embed.add_field(name=infos.text_data["game.creator"],
                        value=infos.message.author.mention,
                        inline=False)
        embed.set_footer(text=infos.text_data["game.tic-tac-toe.entry.footer"])

        message = await infos.client.send_message(
            infos.message.channel,
            embed=embed
        )

        second_player = await wait_for_player(infos, message)

        if second_player is not None:
            await infos.client.delete_message(
                message
            )
            player_dict[channel_id].append(
                second_player
            )
            await infos.client.send_message(
                infos.message.channel,
                player_dict[channel_id][0].mention + " : ❌\n" + player_dict[channel_id][1].mention + " : ⭕"
            )
            await start(infos)
        else:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["game.tic-tac-toe.inactivity.cancel"]
            )
    else:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["game.tic-tac-toe.error.already_launched"]
        )
