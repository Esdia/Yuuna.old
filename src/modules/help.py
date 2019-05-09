from discord import Embed
from src.utils.navigate import navigate


# Given the message, this function determines what to do (general help, or help on a specific game)
async def interpret(infos):
    msg = infos.message.content.split()
    if len(msg) == 1:
        await help_general(infos)
    else:
        func_list = {
            "tic-tac-toe": help_tic_tac_toe,
            "ttt": help_tic_tac_toe,
            "connect4": help_connect4,
            "blackjack": help_blackjack,
            "bj": help_blackjack,
            "chess": help_chess
        }

        if msg[1] in func_list:
            function = func_list[msg[1]]
            await function(infos)
        else:
            """
                For example if you type `y!help games` we want to print the general
                help, but starting from the 6th page
            """
            modules_dict = {
                "misc": 1,
                "miscellaneous": 1,
                "divers": 1,  # French for miscellaneous

                "conf": 2,
                "config": 2,
                "configuration": 2,

                "xp": 3,
                "level": 3,

                "bank": 4,
                "shop": 4,

                "games": 5,
                "jeux": 5,  # French for games

                "mod": 6,
                "moderation": 6,

                "about": 7,
                "contact": 7
            }

            if msg[1].lower() in modules_dict:
                await help_general(infos, first=modules_dict[msg[1]])
            else:
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["info.error.syntax"]
                )


# This function creates a list of embed messages, one for each page
def format_embed(text_data, prefix, game=None):
    list_pages = []
    if game is None:
        title_key = "help.page.{}.{}"
        key = "help.page.{}.field_{}_{}"
    else:
        title_key = "game.{0}.help.page.{1}.{1}".format(
            game,
            "{}"
        )
        key = "game.{0}.help.page.{1}.field_{1}_{1}".format(
            game,
            "{}"
        )

    nb_pages = 0
    while title_key.format(nb_pages+1, "title") in text_data:
        nb_pages += 1

    i = 1
    while title_key.format(i, "title") in text_data:
        page = Embed(title=text_data[title_key.format(i, "title")],
                     description=text_data[
                         title_key.format(
                             i,
                             "description"
                         )
                     ].format(prefix),
                     color=0xD828D0)

        k = 1
        while key.format(i, "value", k) in text_data:
            value = text_data[
                key.format(
                    i,
                    "value",
                    k
                )
            ]
            formats = 0
            for s in range(len(value)-1):
                if value[s:s+2] == "{}":
                    formats += 1
            format_tup = ()
            for _ in range(formats):
                format_tup += (prefix,)

            page.add_field(name=text_data[key.format(i, "name", k)],
                           value=value.format(*format_tup, player="{player}", level="{level}"),
                           inline=False)

            k += 1

        page.set_footer(text=text_data["embed.footer"].format(
            i,
            nb_pages
        ))
        list_pages.append(page)
        i += 1
    return list_pages


async def help_general(infos, first=0):
    list_pages = format_embed(
        infos.text_data,
        infos.prefix
    )

    message_help = await infos.client.send_message(
        infos.message.channel,
        embed=list_pages[first]
    )
    await navigate(
        infos.client,
        message_help,
        infos.message.author,
        list_pages,
        first=first
    )


async def help_tic_tac_toe(infos):
    list_pages = format_embed(
        infos.text_data,
        infos.prefix,
        game="tic-tac-toe"
    )
    await infos.client.send_message(
        infos.message.channel,
        embed=list_pages[0]
    )


async def help_connect4(infos):
    list_pages = format_embed(
        infos.text_data,
        infos.prefix,
        game="connect4"
    )
    await infos.client.send_message(
        infos.message.channel,
        embed=list_pages[0]
    )


async def help_blackjack(infos):
    list_pages = format_embed(
        infos.text_data,
        infos.prefix,
        game="blackjack"
    )
    await infos.client.send_message(
        infos.message.channel,
        embed=list_pages[0]
    )


async def help_chess(infos):
    list_pages = format_embed(
        infos.text_data,
        infos.prefix,
        game="chess"
    )

    message_help = await infos.client.send_message(
        infos.message.channel,
        embed=list_pages[0]
    )
    await navigate(
        infos.client,
        message_help,
        infos.message.author,
        list_pages
    )
