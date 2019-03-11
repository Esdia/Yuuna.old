from discord import Embed

from src.modules.game.blackjack.init import Player, Deck, wait_for_players

"""
    This modules manage a game of Black Jack
"""

channel_list = []


# Determines the winner(s)
def winners(players):
    winner_score = 0
    for p in players:
        if 21 >= p.score > winner_score:
            winner_score = p.score
    win = [p.user for p in players if p.score == winner_score]
    return win


# Called to end the game
async def end(infos, players, message, embed):
    win = winners(players)
    if len(win) == 0:
        phrase = infos.text_data["game.no_winner"]
    elif len(win) == 1:
        phrase = infos.text_data["game.winner"].format(
            win[0].mention
        )
    else:
        phrase = infos.text_data["game.winners"].format(
            ", ".join(win)
        )

    await infos.client.clear_reactions(message)
    score_str = ""
    for p in players:
        score_str += "{} : {}\n".format(
            p.user.mention,
            p.score
        )
    score_str += phrase

    embed.clear_fields()
    embed.add_field(
        name=infos.text_data["game.blackjack.end"],
        value=score_str,
        inline=False
    )
    embed.set_footer(text="")
    await infos.client.edit_message(
        message,
        embed=embed
    )


def game_done(players):
    return not any(p.in_game for p in players)


def turn_done(players):
    return not any(not p.turn_done for p in players)


# Returns a reader-friendly string to show which players have yet to play
def create_printable_turn(players):
    printable = ""
    for p in players:
        emote = "❎"
        if p.turn_done:
            emote = "✅"
        printable += "{} : {}\n".format(
            p.user.mention,
            emote
        )
    return printable


# Returns the number of players which have played their turn
def number_done(players):
    i = 0
    for p in players:
        if p.turn_done:
            i += 1
    return i


async def update_embed(infos, players, message, embed, n):
    embed.clear_fields()
    embed.add_field(
        name="{} n° {}".format(
            infos.text_data["game.blackjack.turn"],
            n
        ),
        value=create_printable_turn(players),
        inline=False
    )
    embed.set_footer(text="{}/{}".format(
        number_done(players),
        len(players)
    ))
    await infos.client.edit_message(
        message,
        embed=embed
    )


# The 'players' list contains a bunch of Players objects, this function returns a list of the users of these Players if they did not chose to stand (i.e. if they are still in_game
def get_player_users(players):
    users = []
    for p in players:
        if p.in_game:
            users.append(p.user)
    return users


# Send in private message the infos about the hand of a player
async def send_score(infos, p):
    embed = Embed(
        title="Black Jack",
        description="",
        color=0xD828D0
    )
    embed.add_field(
        name=infos.text_data["game.hand.cards"],
        value=p.printable_hand(),
        inline=False
    )
    embed.add_field(
        name=infos.text_data["game.hand.score"],
        value=str(p.score),
        inline=False
    )
    await infos.client.send_message(
        p.user,
        embed=embed
    )


# Manages a game turn
async def turn(infos, players, deck, message, embed, n):
    reactions = ["🇭", "🇸"]
    await infos.client.clear_reactions(message)

    for r in reactions:
        await infos.client.add_reaction(message, r)

    await update_embed(infos, players, message, embed, n)

    users = get_player_users(players)
    while not turn_done(players):
        res = await infos.client.wait_for_reaction(
            reactions,
            timeout=120,
            message=message
        )
        # If res has timed out, we kick all the players which have not played. We still want to count them at the end, so we consider them as standing
        if res is None:
            for p in players:
                if not p.turn_done:
                    await infos.client.send_message(
                        infos.message.channel,
                        infos.text_data["game.blackjack.inactivity.kick"].format(p.user.mention)
                    )
                    p.in_game = False
                p.turn_done = True
        elif res.user in users:
            for p in players:
                if p.user == res.user:
                    p.turn_done = True
                    if res.reaction.emoji == "🇸":
                        p.in_game = False
                    users.remove(p.user)
                    await infos.client.remove_reaction(
                        message,
                        res.reaction.emoji,
                        res.user
                    )
        await update_embed(
            infos,
            players,
            message,
            embed,
            n
        )

    # There, every in_game player chose to hit, the other chose to stand
    # So we give a card to all the in_game players, and we see if they have lost of no
    for p in players:
        if p.in_game:
            p.hand.append(
                deck.pick(1)[0]
            )
            p.update_score()
            if p.score > 21:
                p.in_game = False
            else:
                p.turn_done = False
            await send_score(
                infos,
                p
            )


# Manages a full game
async def game(infos, players, deck, message, embed):
    i = 1
    while not game_done(players):
        await turn(
            infos,
            players,
            deck,
            message,
            embed,
            i
        )
        i += 1

    await end(
        infos,
        players,
        message,
        embed
    )


# Manages the first turn (giving 2 cards)
async def first_turn(infos, players, deck, message, embed):
    for p in players:
        p.hand = deck.pick(2)
        p.update_score()
        await send_score(infos, p)
    await game(
        infos,
        players,
        deck,
        message,
        embed
    )


# Creates the deck and starts the game
async def start(infos, players, message, embed):
    deck = Deck(
        len(players) // 2,
        infos.text_data
    )
    await first_turn(
        infos,
        players,
        deck,
        message,
        embed
    )


# First function called when someone use the "y!blackjack" command.
async def create(infos):
    channel_id = infos.message.channel.id
    # channel_list is a list of all the channel currently playing a game
    if channel_id in channel_list:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["game.blackjack.error.already_created"]
        )
    else:
        channel_list.append(channel_id)

        players = [
            Player(infos.message.author)
        ]

        embed_players = Embed(title="Black Jack",
                              description="",
                              color=0xD828D0)
        embed_players.add_field(name=infos.text_data["game.creator"],
                                value=players[0].user.mention,
                                inline=False)
        embed_players.set_footer(text=infos.text_data["game.blackjack.entry.footer"])

        message_players = await infos.client.send_message(
            infos.message.channel,
            embed=embed_players
        )

        players = await wait_for_players(
            infos,
            message_players,
            embed_players,
            players
        )

        if players is None:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["game.blackjack.inactivity.cancel"]
            )
        else:
            await start(
                infos,
                players,
                message_players,
                embed_players
            )

    channel_list.remove(channel_id)
