import discord
from discord.ext import commands
from TOKEN import TOKEN
import os
import sqlite3
import time
import matplotlib.pyplot as plt
import numpy as np
intents = discord.Intents.default()  # Create a default intents object

#TODO:add a test database
#TODO: add a way to save a database


# Add the specific intents your bot needs
intents.message_content = True  # Allows reading message content
#intents.message_reactions = True  # Allows reacting to messages




bot = commands.Bot(command_prefix='!', intents=intents)

def GraphWeight():
    conn = sqlite3.connect('weight.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM weights ORDER BY Timestamp ASC;''')
    data = c.fetchall()
    conn.close()
    weights = [x[0] for x in data]
    times = [x[1] for x in data]

    #fits (can consider doing more polynomial fits later)
    for i in range(1,3):
        coeff = np.polyfit(times, weights, i)
        x = np.linspace(min(times), max(times), 100)
        Polynomial = np.polyval(coeff, x)
        plt.plot(x, Polynomial,color = f"C{i}",  label = f'polyfit of {i} degree')

    plt.plot(times, weights , color = "C0" ,marker='x',label='weight')
    plt.xlabel('Time')
    plt.ylabel('Weight')
    plt.title('Weight vs Time')
    plt.legend(loc='best')

    plt.savefig('weight.png')
    plt.close()
    return True

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    target_channel = discord.utils.get(message.guild.channels, name="weightcheck")
    if message.channel == target_channel:
        await message.add_reaction('🔄')

        try:
            weight = float(message.content)
            current_time = time.time()
            conn = sqlite3.connect('weight.db')
            c = conn.cursor()
            c.execute('''INSERT INTO weights (weight, Timestamp) VALUES (?, ?)''', (weight, current_time))
            conn.commit()
            conn.close()
            await target_channel.send(f"Weight: {weight} \n Time: {current_time} \n Added to database.")
            await message.remove_reaction('🔄', bot.user)
            await message.add_reaction('✅')
            

            if GraphWeight(): #TODO: this is done in a weird way, needs a refactor
                with open("weight.png", "rb") as f:
                    image = discord.File(f)
                await target_channel.send(file = image)
                f.close()
                os.remove("weight.png") #we want to error out if this fails

            else:
                await target_channel.send("Error: Couldn't generate the graph.")
            
        except Exception as e:
            await message.remove_reaction('🔄', bot.user)
            await message.add_reaction('❌')
            await target_channel.send(f"Error: {e}")
            
        
        
        
        


bot.run(TOKEN)
