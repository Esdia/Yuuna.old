from discord import Embed

from src.utils.game import wait_for_player

emotes = {
    "red": "🔴",
    "blue": "🔵",
    "black": "⚫"
}


class Chip:
    def __init__(self, color="black"):
        self.color = color
        if color in emotes:
            self.emote = emotes[color]
        else:
            self.emote = emotes["black"]


class Game:
    def __init__(self, players, message, embed):
        self.grid = self.create_grid()
        self.players = players
        self.turn = players[0]
        self.winner = None
        self.message = message
        self.embed = embed
        self.reactions = [
            "1⃣",
            "2⃣",
            "3⃣",
            "4⃣",
            "5⃣",
            "6⃣",
            "7⃣"
        ]
        self.colors = [
            "red",
            "blue"
        ]

    @staticmethod
    def create_grid():
        black_circle = Chip("black")
        grid = []
        for _ in range(7):
            line = []
            for _ in range(7):
                line.append(black_circle)
            grid.append(line)
        return grid

    @staticmethod
    def in_bounds(i, j):
        return 0 <= i <= 6 and 0 <= j <= 6

    def win(self):
        directions = [
            (1, 1),
            (1, 0),
            (1, -1),
            (0, 1),
            (0, -1),
            (-1, 1),
            (-1, 0),
            (-1, -1)
        ]
        for i in range(7):
            for j in range(7):
                if self.grid[i][j].color != "black":
                    chip = self.grid[i][j]
                    for (a, b) in directions:
                        i_temp, j_temp = i, j
                        won = True
                        for _ in range(3):
                            i_temp += a
                            j_temp += b
                            if not self.in_bounds(i_temp, j_temp) or (chip.color != self.grid[i_temp][j_temp].color):
                                won = False
                                break
                        if won:
                            if chip.color == "red":
                                return self.players[0]
                            else:
                                return self.players[1]
        return None

    def create_printable(self):
        printable = ""
        for i in range(6, -1, -1):
            line = ""
            for j in range(0, 7):
                line += "{}".format(
                    self.grid[i][j].emote
                )
            printable += "{}\n".format(line)
        printable += "1⃣2⃣3⃣4⃣5⃣6⃣7⃣"
        return printable


async def init(infos):
    embed = Embed(title=infos.text_data["game.connect4.name"],
                  description="",
                  color=0xD828D0)
    embed.add_field(name=infos.text_data["game.creator"],
                    value=infos.message.author.mention,
                    inline=False)
    embed.set_footer(text=infos.text_data["game.connect4.entry.footer"])

    message = await infos.client.send_message(
        infos.message.channel,
        embed=embed
    )

    second_player = await wait_for_player(infos, message)
    if second_player is None:
        return None
    else:
        return (
            Game(
                [
                    infos.message.author,
                    second_player,
                ],
                message,
                embed
            )
        )
