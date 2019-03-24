from discord import Embed
from src.utils.navigate import navigate


# Given the message, this function determines what to do (general help, or help on a specific game)
async def interpret(infos):
    msg = infos.message.content.split()
    if len(msg) == 1:
        await help_general(infos)
    else:
        func_list = {"tic-tac-toe": help_tic_tac_toe,
                     "ttt": help_tic_tac_toe,
                     "connect4": help_connect4,
                     "blackjack": help_blackjack,
                     "bj": help_blackjack,
                     "chess": help_chess}

        if msg[1] in func_list:
            function = func_list[msg[1]]
            await function(infos)
        else:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["info.error.syntax"]
            )


# Given the number of fields for each page, this function creates a list of embed messages, one for each page
def format_embed(nb_fields, text_data, prefix, game=None):
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
    for i in range(len(nb_fields)):
        page = Embed(title=text_data[title_key.format(i+1, "title")],
                     description=text_data[
                         title_key.format(
                             i+1,
                             "description"
                         )
                     ].format(prefix),
                     color=0xD828D0)
        fields = nb_fields[i]
        for k in range(1, fields+1):
            value = text_data[
                key.format(
                    i+1,
                    "value",
                    k
                )
            ]
            formats = 0
            for s in range(len(value)-1):
                if value[s:s+2] == "{}":
                    formats += 1
            format_tup = (prefix,)
            for _ in range(formats-1):
                format_tup += format_tup

            page.add_field(name=text_data[key.format(i+1, "name", k)],
                           value=value.format(*format_tup),
                           inline=False)
        page.set_footer(text=text_data["embed.footer"].format(
            i+1,
            len(nb_fields)
        ))
        list_pages.append(page)
    return list_pages


async def help_general(infos):
    nb_fields = [2, 3, 2, 2, 2, 4, 4, 3]
    list_pages = format_embed(
        nb_fields,
        infos.text_data,
        infos.prefix
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


async def help_tic_tac_toe(infos):
    nb_fields = [2]
    list_pages = format_embed(
        nb_fields,
        infos.text_data,
        infos.prefix,
        game="tic-tac-toe"
    )
    await infos.client.send_message(
        infos.message.channel,
        embed=list_pages[0]
    )


async def help_connect4(infos):
    nb_fields = [2]
    list_pages = format_embed(
        nb_fields,
        infos.text_data,
        infos.prefix,
        game="connect4"
    )
    await infos.client.send_message(
        infos.message.channel,
        embed=list_pages[0]
    )


async def help_blackjack(infos):
    nb_fields = [3]
    list_pages = format_embed(
        nb_fields,
        infos.text_data,
        infos.prefix,
        game="blackjack"
    )
    await infos.client.send_message(
        infos.message.channel,
        embed=list_pages[0]
    )


async def help_chess(infos):
    nb_fields = [2, 6, 2, 2]
    list_pages = format_embed(
        nb_fields,
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
