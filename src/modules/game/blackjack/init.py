from random import randint

"""
   This module contains the definitions of the classes used for the Black Jack game,
   and it manages the initialisation of the game 
"""


class Player:
    def __init__(self, user):
        self.user = user
        self.score = 0
        self.hand = []
        self.turn_done = False
        self.in_game = True

    def update_score(self):
        aces = 0
        temp_score = 0
        for c in self.hand:
            # In english and in french, "Ace" starts with an 'A'
            if c[0] == 'A':
                aces += 1
            elif c.split()[0].isdigit():
                temp_score += int(c.split()[0])
            else:
                temp_score += 10
        if aces > 0:
            # No matter how many aces you have, the sum of their value is either n or n+10
            temp_score += aces
            if temp_score + 10 <= 21:
                temp_score += 10
        self.score = temp_score

    def printable_hand(self):
        printable = ""
        for c in self.hand:
            printable += "{}\n".format(c)
        return printable


class Deck:
    def __init__(self, n, text_data):
        self.deck = []
        self.n = n
        self.text_data = text_data
        self.create()

    @staticmethod
    def one_deck(text_data):
        suits = [
            text_data["game.cards.suit.spades"],
            text_data["game.cards.suit.diamonds"],
            text_data["game.cards.suit.hearts"],
            text_data["game.cards.suit.clubs"]
        ]
        heads = [
            text_data["game.cards.head.jack"],
            text_data["game.cards.head.queen"],
            text_data["game.cards.head.king"],
            text_data["game.cards.head.ace"]
        ]
        deck = []
        linking_word = text_data["game.cards.linking_word"]
        for s in suits:
            for i in range(2, 11):
                deck.append("{} {} {}".format(
                    i,
                    linking_word,
                    s
                ))
            for h in heads:
                deck.append("{} {} {}".format(
                    h,
                    linking_word,
                    s
                ))
        return deck

    def create(self):
        temp_big_deck = []
        deck = self.one_deck(self.text_data)

        for _ in range(self.n):
            temp_big_deck.extend(deck)

        while len(temp_big_deck) > 0:
            i = randint(
                0,
                len(temp_big_deck) - 1
            )
            self.deck.append(
                temp_big_deck.pop(i)
            )

    def pick(self, n):
        res = []
        for _ in range(n):
            if len(self.deck) == 0:
                self.create()
            res.append(
                self.deck.pop(0)
            )
        return res


def signed_in(player, player_list):
    return any(p.user == player for p in player_list)


async def wait_for_players(infos, message, embed, players):
    reactions = ["▶", "🇯"]
    for r in reactions:
        await infos.client.add_reaction(
            message,
            r
        )

    # ok = True if at least 2 players
    ok = False
    start = False
    str_players = ""

    while not (ok and start):
        res = await infos.client.wait_for_reaction(
            reactions,
            message=message,
            timeout=120
        )
        if res is None:
            if infos.manage_message:
                await infos.client.clear_reactions(
                    message
                )
            return None
        elif not res.user.bot:
            react = res.reaction.emoji
            user = res.user
            # i.e. join
            if react == reactions[1] and not signed_in(user, players):
                players.append(
                    Player(user)
                )
                str_players += "{}\n".format(user.mention)
                if len(players) == 2:
                    embed.add_field(
                        name=infos.text_data["game.blackjack.players"],
                        value=str_players,
                        inline=False
                    )
                else:
                    embed.set_field_at(
                        1,
                        name=infos.text_data["game.blackjack.players"],
                        value=str_players,
                        inline=False
                    )
                await infos.client.edit_message(
                    message,
                    embed=embed
                )
                # There are at least 2 players, so we are okay to go
                ok = True
            # start
            elif react == reactions[0]:
                if infos.manage_messages:
                    await infos.client.remove_reaction(
                        message,
                        react,
                        user
                    )
                if user == players[0].user:
                    start = True

    if infos.manage_message:
        await infos.client.clear_reactions(
            message
        )

    return players
