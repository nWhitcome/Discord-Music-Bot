import os
import discord
from dotenv import load_dotenv
from discord.ext.commands import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
import sqlite3
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
suggChannel = '839962435044900874'
testChannel = '840042019971661825'

bot = Bot(command_prefix='$')
dictionary = {}

# Sends out a poll so people can vote on album of the week
async def sendPoll():
    print("Posting poll...")
    channel = bot.get_channel(839961783498571867)
    pollString = '/poll "<@&839958672868245504>, here is the poll for the album of the week:"'
    for i, j in dictionary.items():
        pollString += f' "{i} - {j}"'
    await channel.send(pollString)
    async for message in channel.history(limit = 10):
        if message.author == bot.user:
            await message.delete()
            break
    dictionary.clear()

    # Deletes all of the previous week's suggestions
    conn = sqlite3.connect('weeklyData.db')
    c = conn.cursor()
    c.execute('DELETE FROM weekly;')
    conn.commit()

# Allows users to submit a suggestion for album of the week, which is then stored in a database
@bot.command(name='suggest')
async def suggest(ctx, *, arg):
    print("Received suggestion")
    if(str(ctx.channel.id) == suggChannel or str(ctx.channel.id) == testChannel):
        dictionary[ctx.author] = arg
        conn = sqlite3.connect('weeklyData.db')
        c = conn.cursor()
        c.execute('INSERT INTO weekly(id, content) VALUES(?,?);', (str(ctx.author), str(arg)))
        conn.commit()
        await ctx.message.add_reaction("👍")

# Lists all of the album choices that have been submitted
@bot.command(name='list')
async def listSuggestions(ctx):
    print("Listing suggestions")
    if(str(ctx.channel.id) == suggChannel or str(ctx.channel.id) == testChannel):
        for k, v in dictionary.items():
            await ctx.send(f'{k} - {v}')

# Backup method that can only be called in the TestBot server that puts the album choice poll up in case it fails for some reason
@bot.command(name='poll')
async def poll(ctx):
    if(str(ctx.channel.id) == testChannel):
        await sendPoll()

# Backup method that can only be called in the TestBot server that chooses the winner
@bot.command(name='choosethewinner')
async def choosethewinner(ctx):
    if(str(ctx.channel.id) == testChannel):
        chooseWinner()

# Chooses a winner from the album poll on the Covid Club server
async def chooseWinner():
    channel = bot.get_channel(839961783498571867)

    # Finds the last poll posted in the music announcements channel and gets the winner. Myself and the admins are the only ones that can post in that channel.
    async for message in channel.history(limit = 10):
        if message.author.id == 324631108731928587:
            max = 0
            index = []
            i = 0
            while i <  len(message.reactions):
                if(int(message.reactions[i].count) > max):
                    max = message.reactions[i].count
                    index = [i]
                elif message.reactions[i].count == max:
                    index.append(i)
                i = i+1
            await channel.send('<@&839958672868245504> And the winning album for the week is:')

            # Breaks ties with the random function
            await channel.send(message.embeds[0].description.split("\n")[random.choice(index)])
            await channel.send("Suggestions are now open for the following week, so make sure to get them in by Saturday at 2 PM CST!")
            break

@bot.event
async def on_ready():
    print("Ready")
    conn = sqlite3.connect('weeklyData.db')
    makeTable = 'CREATE TABLE IF NOT EXISTS weekly (id text PRIMARY KEY, content text NOT NULL); '

    c = conn.cursor()
    c.execute(makeTable)
    c.execute('SELECT * FROM weekly;')

    rows = c.fetchall()
    for row in rows:
        dictionary[row[0]] = row[1]

    scheduler = AsyncIOScheduler()
    scheduler.add_job(sendPoll, 'cron', day_of_week='sat', hour=2)
    scheduler.add_job(chooseWinner, 'cron', day_of_week='sun', hour=2)
    scheduler.start()

bot.run(TOKEN)