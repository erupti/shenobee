import os
import discord
import re
import asyncio
import random
import traceback
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# Loading stuff
token = os.environ.get("token")
client = discord.Client()
guild = df = None

notAuthMsg = "You're not authorized to use this command."
errorMsg = "An error occurred. Please make sure you\'re using the command correctly and try again."


#  Opening files
df = pd.read_csv("df.csv", index_col=0)
with open("clowns.txt") as file:
    clownList = file.read().splitlines()


# Prints login message to console when the bot is connected and ready. Also gets the server to connect to.
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    global guild
    guild = client.get_guild(int(os.environ.get("serverID")))


@client.event
async def on_message(message):
    global df, guild
    try:
        # Ignore own messages
        if message.author.id == 740802427363786821:
            return

        # Check if message is a command
        elif message.content.startswith('%'):
            # Confirmed that they're in a guild, so now get the first part of the command
            splitMessage = message.content.split(" ")

            if splitMessage[0] == "%shutupnobee":
                if "Operator" in map(str, message.author.roles):
                    await message.channel.send(notAuthMsg)
                    return
                idToPing = str(message.mentions[0].id)
                if idToPing == "144207749725552642":
                    await message.channel.send("no u")
                    idToPing = str(message.author.id)
                try:
                    amount = int(splitMessage[2])
                    if amount > 300:
                        amount = 300
                except:
                    amount = 50
                for i in range(amount):
                    msg = await message.channel.send("<@" + idToPing + ">")
                    await msg.delete()
                    await asyncio.sleep(0.8)

            elif splitMessage[0] == "%clown":
                await message.channel.send(random.choice(clownList))

            elif splitMessage[0] == "%coin":
                await coinFlip(message, splitMessage[1].lower(), int(splitMessage[2]))

            elif splitMessage[0] == "%bal" or splitMessage[0] == "%balance":
                if message.author.id not in df.index:
                    await newProfile(message, message.author.id)
                await message.channel.send("You have " + str(df.at[message.author.id, "Balance"]) + " moneys.")

            elif splitMessage[0] == "%DICK!":
                idToAdd = message.mentions[0].id
                if idToAdd not in df.index:
                    await newProfile(message, idToAdd)
                df.at[idToAdd, "Dicks"] += 1
                df.to_csv("df.csv")
                await message.channel.send("Thank you for reporting, comrade! One dick joke count has been added to <@" + str(idToAdd) + ">'s counter.")

            elif splitMessage[0] == "%dickcount":
                try:
                    idToCheck = message.mentions[0].id
                    strStart = message.mentions[0].display_name + " has"
                except:
                    idToCheck = message.author.id
                    strStart = "You've"
                if idToCheck not in df.index:
                    await message.channel.send("That user is not registered.")
                else:
                    await message.channel.send(strStart + " made " + str(df.at[idToCheck, "Dicks"]) + " dick jokes so far. That I know of...")

            elif splitMessage[0] == "%mercy":
                if message.author.id not in df.index:
                    await newProfile(message, message.author.id)
                if df.at[message.author.id, "Balance"] < 1:
                    df.at[message.author.id, "Balance"] = 1000
                    await message.channel.send("Wow, you're *broke* broke. Here's 1000 moneys.")
                    df.to_csv("df.csv")
                else:
                    await message.channel.send("Eh, you'll be fine...")


        # Fun little function, also useful to check if bot is up, check bot permissions, etc
        elif client.user in message.mentions:
            await message.channel.send('<a:KannaPingNom:727138651615789158>')


        elif "fortnite" in message.content:
            await message.channel.send(chugJug)
        elif "fortvide" in message.content:
            await message.channel.send(fortvide)
        elif "capperu" in message.content or "caperu" in message.content:
            await message.channel.send(copypasta)
        elif "thicc" in message.content:
            await message.channel.send(thiccBoy)

        # elif message.channel == mainChat and message.author.id != 740802427363786821:
        #    try:
        #        await aprilFools(message.author)
        #    except:
        #        pass

    except Exception:
        await message.channel.send(errorMsg)
        print(traceback.format_exc())


# April fools function!
async def aprilFools(user):
    name = user.display_name
    name = re.sub(' +',' ', name)
    name = name.replace('.','')
    if len(name) <= 30:
        vowelList = "aeiouAEIOU"
        upperVowelList = "AEIOU"
        index = -1

        for letter in name:
            if letter in vowelList:
                index = name.index(letter)
                break

        if index <= 0:
            name += "Eru"
        elif name[index+1] in vowelList:
            name = "".join((name[:index], "eru", name[index+2:]))
        elif name[index] in upperVowelList:
            name = "".join((name[:index], "Eru", name[index+1:]))
        else:
            name = "".join((name[:index], "eru", name[index+1:]))

        await user.edit(nick=name)


async def newProfile(message, id):
    global df
    newDF = pd.DataFrame({"Balance": [10000], "Dicks": [0]}, index=[id])
    print("New profile created for", id)
    await message.channel.send("New profile created for <@" + str(id) + ">.")
    df = pd.concat([df, newDF], axis=0)
    df.to_csv("df.csv")


async def coinFlip(message, choice, wager):
    global df
    id = message.author.id
    if id not in df.index:
        await newProfile(message, message.author.id)

    if df.at[id, "Balance"] < wager:
        await message.channel.send("You're too poor for that... You only have " + str(df.at[id, "Balance"]) + "!")
        return

    if choice == "t":
        choice = "tails"
    elif choice == "h":
        choice = "heads"
    elif choice != "tails" and choice != "heads":
        return "The coin is confused by your choice and asks you to pick an actual side."

    outcome = random.choice(["tails", "heads"])
    await message.channel.send("The coin landed on " + outcome + ".")
    if choice == outcome:
        await message.channel.send("You won " + str(wager) + " moneys!")
        df.at[id, "Balance"] += wager
    else:
        if df.at[id, "Balance"] * 0.8 <= wager and random.choice([True, True, False, False, False]):
            webhook = await message.channel.create_webhook(name="Coin")
            await webhook.send("Wait! Friend! Everything's on the line, we can't lose here! With the power of friendship, I can...!",
                               username="Coin")
            outcome = random.choice(["tails", "heads"])
            await message.channel.send("The coin miraculously flips in the air, and lands on...\n" +
                                       outcome.capitalize() + ".")
            if choice == outcome:
                await message.channel.send("You won " + str(wager) + " moneys!")
                df.at[id, "Balance"] += wager * 2
            else:
                await message.channel.send("You lost " + str(wager) + " moneys...")
        else:
            await message.channel.send("You lost " + str(wager) + " moneys...")
        df.at[id, "Balance"] -= wager
    df.to_csv("df.csv")
    

chugJug = "We got a number one Victory Royale\nYeah, Fortnite, we 'bout to get down (get down)\nTen kills on the board right now\nJust wiped out Tomato Town\nMy friend just got downed\nI revived him, now we're heading south-bound\nNow we're in the Pleasant Park streets\nLook at the map, go to the marked sheet\nTake me to your Xbox to play Fortnite today\nYou can take me to Moisty Mire, but not Loot Lake\nI really love to Chug Jug with you\nWe can be pro Fortnite gamers\nHe said\nHey broski, you got some heals and a shield pot?\nI need healing and I am only at one HP\nHey dude, sorry, I found nothing on this safari\nI checked the upstairs of that house but not the underneath yet\nThere's a chest that's just down there\nThe storm is coming fast and you need heals to prepare\nI've got V-Bucks that I'll spend\nMore than you can content\nI'm a cool pro Fortnite gamer (cool pro Fortnite-)\nTake me to your Xbox to play Fortnite today\nYou can take me to Moisty Mire, but not Loot Lake\nI really love to Chug Jug with you\nWe can be pro Fortnite gamers\nLa-la-la-la-la-e-ya\nLa-la-la-la-la-e-ya\nLa-la-la-la-la-e-ya\nWill you be my pro Fortnite gamer? (Pro Fortnite gamer)\nCan we get a win this weekend?\nTake me to Loot Lake\nLet's change the game mode and we can Disco Dominate\nLet's hop in an ATK\nTake me to the zone\nI'm running kind of low on meds, I need to break some stone\nDressed in all his fancy clothes\nHe's got Renegade Raider and he's probably a pro\nHe just shot my back\nI turn back and I attack\nI just got a Victory Royale\nA Victory Royale\nTake me to your Xbox to play Fortnite today\nYou can take me to Moisty Mire, but not Loot Lake\nI really love to Chug Jug with you\nWe can be pro Fortnite gamers"
fortvide = "I miss the old Fortnite,\ndavid big nub Fortnite,\nthe uncontrolled Fortnite,\ndavid big nub Fortnite,\nthe paper-gold Fortnite,\ndavid big nub Fortnite,\nthe unsold Fortnite,\ndavid big nub Fortnite,\nI hate the new Fortnite,\ndavid big nub Fortnite,\nthe pro noob Fortnite,\ndavid big nub Fortnite,\nthe always 'new' Fortnite,\ndavid big nub Fortnite,\nthe Twitter news Fortnite,\ndavid big nub Fortnite,\nI miss the dope Fortnite,\ndavid big nub Fortnite,\nthe rising slope Fortnite,\ndavid big nub Fortnite,\nI gotta say, at that time I liked to play Fortnite,\nsee I first started Fortnite,\nI used to slay Fortnite,\nand now I shoot and shoot around and It's just 8's Fortnite,\ndavid big nub Fortnite,\nI used to love Fortnite,\nI used to love Fortnite,\nI even had the Skull trooper, thought I was Fortnite,\nwhat If david big nub Fortnite, made a song about Fortnite, called 'I miss the old Fortnite' old school Fortnite,\nand what I was Fortnite\nWe still love Fortnite, and I love you like Fortnite loves Fortnite\ndavid big nub Fortnite,\nWe still love Fortnite, and I love you like Fortnite loves Fortnite\ndavid big nub Fortnite,\nWe still love Fortnite, and I love you like Fortnite loves Fortnite"
copypasta = "What in the mighty gods' names did you just say about me, you little worm? I'll let you know that I am the foremost soldier of this land created by Hengist and Horsa and unified by Alfred, and I took part in many battles against foul foreign non-believers who will build their churchhouses and so sully our land, and I have killed over 300 Grendels with my hands. I have knowledge of all manners of battle and am the mightiest shot in all of England's army because of the gods. For me you are nothing but a little animal which my arrow pierces. I will kill you with ability given to me by Woden, the likes of which have never before been seen on this earth, may Woden hear my words. You think that you can say such to me, when the gods chose me to defend this land? Think again, enemy. As we speak my prayers arrive in the heavens, and Woden gathers his soldiers over all of England, and the gods know your name, so prepare yourself for the storm, worm. The storm which will end the laughable thing that you call your life. You are dead to the earth and heavens, child. Because of the gods I may be anywhere, anytime, and I can kill you in over 700 ways, and that with only my bare hands. I have wide knowledge of weaponless combat and also the heavens are with me, and I will use them fully to cleanse Britain of you, you little shit. If you just knew what you recieve from all the gods and folk, you would hold your speech. But you couldn't, you didn't, and now pay for that, you of weak thought. Heaven has given you up and I will do my worst. You are dead to the earth and heavens, kid."
thiccBoy = "currently wondering why my mom slapped my butt like I was a girl <:WorryThink:807427294570348567> am I a girl? Because she called me thicc so ig im a thicc boy now"

client.run(token)
