from discord import Embed


async def navigate_query(infos, message, list_pages, reactions, results):
    i = 0  # index of the current page
    maxi = len(list_pages)

    # We have one page -> we remove the navigation arrows
    if maxi == 1:
        for react in reactions:
            react.pop(0)
            react.pop(0)

    for r in reactions[0]:
        await infos.client.add_reaction(message, r)

    res = await infos.client.wait_for_reaction(
        reactions[0],
        message=message,
        user=infos.message.author,
        timeout=60
    )

    while res is not None:
        r = res.reaction.emoji
        if r == '⬅':
            if i > 0:
                i -= 1
            # If we try to go left from the first page, we end up on the last one
            else:
                i = maxi - 1
        elif r == '➡':
            if i < maxi - 1:
                i += 1
            # If we try to go right from the last page, we end up on the first one
            else:
                i = 0
        else:
            res_index = reactions[i].index(r) - 2
            # If we have only one page, we cut off the arrows in the reactions
            # So to get the role index, we have to add 2 again
            if maxi == 1:
                res_index += 2
            await infos.client.delete_message(message)
            return results[i * 10 + res_index]
        if infos.manage_messages:
            await infos.client.remove_reaction(
                message,
                r,
                infos.message.author
            )
        await infos.client.edit_message(
            message,
            embed=list_pages[i]
        )
        res = await infos.client.wait_for_reaction(
            reactions[0],
            message=message,
            user=infos.message.author,
            timeout=60
        )

    if infos.manage_messages:
        await infos.client.clear_reactions(message)
    return None


async def select_result(infos, results):
    reactions_template = [
        '⬅',
        '➡',
        "0⃣",
        "1⃣",
        "2⃣",
        "3⃣",
        "4⃣",
        "5⃣",
        "6⃣",
        "7⃣",
        "8⃣",
        "9⃣"
    ]
    list_pages = []
    reactions = []

    tmp_react = [
        reactions_template[0],
        reactions_template[1]
    ]
    printable = ""

    i = 0
    for a in results:
        printable += "{} {} ({})\n".format(
            reactions_template[i % 10 + 2],
            a["title"],
            a["type"]
        )
        tmp_react.append(reactions_template[i % 10 + 2])
        i += 1
        if i % 10 == 0:
            embed = Embed(
                title=infos.text_data["anime.select"],
                description="",
                color=0xD828D0
            )
            embed.add_field(
                name=infos.text_data["anime.results"],
                value=printable,
                inline=False
            )
            list_pages.append(embed)
            reactions.append(tmp_react)
            tmp_react = [
                reactions_template[0],
                reactions_template[1]
            ]
            printable = ""

    if len(results) == 0:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["anime.no_result"]
        )
        return

    if i % 10 != 0:
        embed = Embed(
            title=infos.text_data["anime.select"],
            description="",
            color=0xD828D0
        )
        embed.add_field(
            name=infos.text_data["anime.results"],
            value=printable,
            inline=False
        )
        list_pages.append(embed)
        reactions.append(tmp_react)

    for i in range(len(list_pages)):
        list_pages[i].set_footer(
            text=infos.text_data["embed.footer"].format(
                current=(i + 1),
                total=len(list_pages)
            )
        )

    message = await infos.client.send_message(
        infos.message.channel,
        embed=list_pages[0]
    )

    return await navigate_query(
        infos,
        message,
        list_pages,
        reactions,
        results
    )


async def favorites(infos, type_, username):
    user = await infos.jikan.user(username=username)
    fav = user["favorites"][type_]
    embed = Embed(
        title="",
        description="",
        color=0xD828D0
    )
    printable = ""
    i = 1
    for f in fav:
        printable += "{} : {}".format(
            i,
            f["name"],
        )
        if type_ == "characters":
            c = await infos.jikan.character(f["mal_id"])
            if len(c["animeography"]) > 0:
                printable += " ({})".format(
                    c["animeography"][0]["name"]
                )
            else:
                printable += " ({})".format(
                    c["mangaography"][0]["name"]
                )
        printable += "\n"
        i += 1

    embed.add_field(
        name=infos.text_data["anime.top10"].format(
            user=username,
            type=type_
        ),
        value=printable
    )
    await infos.client.send_message(
        infos.message.channel,
        embed=embed
    )


async def anime(infos, query):
    result = await infos.jikan.search(search_type="anime", query=query)

    res = await select_result(infos, result["results"])
    if res is None:
        return
    res = await infos.jikan.anime(res["mal_id"])

    embed = Embed(
        title=res["title"],
        description="JP : {}\nEN : {}\nSynonyms : {}".format(
            res["title_japanese"],
            res["title_english"],
            ", ".join(res["title_synonyms"])
        ),
        color=0xD828D0,
        url=res["url"]
    )
    embed.set_image(url=res["image_url"])
    embed.add_field(
        name="Type",
        value=res["type"],
        inline=True
    )
    embed.add_field(
        name="Episodes",
        value=res["episodes"],
        inline=True
    )
    embed.add_field(
        name="Duration",
        value=res["duration"],
        inline=True
    )
    embed.add_field(
        name="Score",
        value=res["score"],
        inline=True
    )
    embed.add_field(
        name="Status",
        value=res["status"],
        inline=True
    )
    embed.add_field(
        name="Season",
        value=res["premiered"],
        inline=True
    )
    embed.add_field(
        name="Source",
        value=res["source"],
        inline=True
    )
    embed.add_field(
        name="Studio",
        value=", ".join(studio["name"] for studio in res["studios"]),
        inline=True
    )
    embed.add_field(
        name="Genre",
        value=", ".join(genre["name"] for genre in res["genres"]),
        inline=True
    )
    if len(res["synopsis"]) > 1000:
        res["synopsis"] = res["synopsis"][:965] + ".. [too long to fit in the message]"
    embed.add_field(
        name="Synopsis",
        value=res["synopsis"][:1000],
        inline=False
    )
    embed.add_field(
        name="Related",
        value="\n".join("{} : {} ({})".format(
            relation,
            res["related"][relation][i]["name"],
            res["related"][relation][i]["type"]
        ) for relation in res["related"] for i in range(len(res["related"][relation]))),
        inline=False
    )
    embed.add_field(
        name="Opening themes",
        value="\n".join(res["opening_themes"]),
        inline=True
    )
    embed.add_field(
        name="Ending themes",
        value="\n".join(res["ending_themes"]),
        inline=True
    )

    await infos.client.send_message(
        infos.message.channel,
        embed=embed
    )


async def manga(infos, query):
    result = await infos.jikan.search(search_type="manga", query=query)

    res = await select_result(infos, result["results"])
    if res is None:
        return
    res = await infos.jikan.manga(res["mal_id"])

    embed = Embed(
        title=res["title"],
        description="JP : {}\nEN : {}\nSynonyms : {}".format(
            res["title_japanese"],
            res["title_english"],
            ", ".join(res["title_synonyms"])
        ),
        color=0xD828D0,
        url=res["url"]
    )
    embed.set_image(url=res["image_url"])
    embed.add_field(
        name="Type",
        value=res["type"],
        inline=True
    )
    if res["publishing"]:
        embed.add_field(
            name="Status",
            value="Publishing",
            inline=True
        )
    else:
        embed.add_field(
            name="Volumes",
            value=res["volumes"],
            inline=True
        )
        embed.add_field(
            name="Chapters",
            value=res["chapters"],
            inline=True
        )
    embed.add_field(
        name="Score",
        value=res["score"],
        inline=True
    )
    embed.add_field(
        name="Genre",
        value=", ".join(genre["name"] for genre in res["genres"]),
        inline=True
    )
    if len(res["synopsis"]) > 1000:
        res["synopsis"] = res["synopsis"][:965] + ".. [too long to fit in the message]"
    embed.add_field(
        name="Synopsis",
        value=res["synopsis"][:1000],
        inline=False
    )
    embed.add_field(
        name="Related",
        value="\n".join("{} : {} ({})".format(
            relation,
            res["related"][relation][i]["name"],
            res["related"][relation][i]["type"]
        ) for relation in res["related"] for i in range(len(res["related"][relation]))),
        inline=False
    )
    await infos.client.send_message(
        infos.message.channel,
        embed=embed
    )


async def interpret(infos):
    msg = infos.message.content.split()
    if len(msg) < 3:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
        return

    if msg[1] == "anime":
        await anime(infos, "".join(msg[2:]))
    elif msg[1] == "manga":
        await manga(infos, "".join(msg[2:]))
    elif msg[1] == "favorites":
        if msg[2] not in ["anime", "manga", "characters", "people"] or len(msg) != 4:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["info.error.syntax"]
            )
            return
        await favorites(infos, msg[2], msg[3])
    else:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
