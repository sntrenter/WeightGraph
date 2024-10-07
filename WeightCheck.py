import discord
from discord.ext import commands
from TOKEN import TOKEN,myUserID
import os
import sqlite3
import time
import matplotlib.pyplot as plt
import numpy as np
intents = discord.Intents.default()  # Create a default intents object

# Add the specific intents your bot needs
intents.message_content = True  # Allows reading message content
#intents.message_reactions = True  # Allows reacting to messages




bot = commands.Bot(command_prefix='!', intents=intents)

def GraphWeight():

    conn = sqlite3.connect('weight.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM weights''')
    data = c.fetchall()
    conn.close()
    weights = [x[0] for x in data]
    times = [x[1] for x in data]
    plt.plot(times, weights)
    plt.xlabel('Time')
    plt.ylabel('Weight')
    plt.title('Weight vs Time')
    plt.savefig('weight.png')
    
    return True

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    # Check if the message is from the bot itself to avoid reacting to its own messages.
    if message.author == bot.user:
        return
    ## Check if the message was sent in the target channel
    target_channel = discord.utils.get(message.guild.channels, name="weightcheck")
    if message.channel == target_channel:
        await message.add_reaction('🔄')#'✅')

        try:
            weight = float(message.content)
            current_time = time.time()
            conn = sqlite3.connect('weight.db')
            c = conn.cursor()
            c.execute('''INSERT INTO weights (weight, Timestamp) VALUES (?, ?)''', (weight, current_time))
            conn.commit()
            conn.close()
            await target_channel.send(f"Weight: {weight} \n Time: {current_time} \n Added to database.")
            await message.add_reaction('✅')

            if GraphWeight():
                with open("weight.png", "rb") as f:
                    image = discord.File(f)
                await target_channel.send(file = image)
                f.close()
                os.remove("weight.png") #we want to error out if this fails

            else:
                await target_channel.send("Error: Couldn't generate the graph.")
            
        except Exception as e:
            await message.add_reaction('❌')
            await target_channel.send(f"Error: {e}")
            
        
        
        
        


bot.run(TOKEN)
