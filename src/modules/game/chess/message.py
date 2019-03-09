"""
    This module manages the board message
"""


# Return a user-friendly board, consisting of emotes
def get_printable(game):
    basic_board = [
        ["⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛"],
        ["⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜"],
        ["⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛"],
        ["⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜"],
        ["⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛"],
        ["⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜"],
        ["⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛"],
        ["⬛", "⬜", "⬛", "⬜", "⬛", "⬜", "⬛", "⬜"]
    ]

    # Letters from c to h are custom emotes on my private server
    emotes_alpha = [
        "🅰",
        "🅱",
        "<:c_:524714347667390475>",
        "<:d_:524714350142029824>",
        "<:e_:524714350053818406>",
        "<:f_:524714350234304514>",
        "<:g_:524714350116732940>",
        "<:h_:524714350087241730>"
    ]

    emotes_num = [
        "8⃣",
        "7⃣",
        "6⃣",
        "5⃣",
        "4⃣",
        "3⃣",
        "2⃣",
        "1⃣",
    ]

    printable = ""
    for x in range(8):
        for y in range(8):
            piece = game.board[x][y]
            if type(piece) is str:
                printable += basic_board[x][y]
            else:
                printable += piece.emote
        printable += emotes_num[x] + "\n"
    printable += "".join(emotes_alpha)
    return printable


# This function updates the message every turn
async def update_message(infos, game):
    await infos.client.delete_message(
        game.message
    )

    message = await infos.client.send_message(
        infos.message.channel,
        get_printable(game)
    )

    game.message = message

