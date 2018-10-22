import discord
import asyncio
import aiohttp
import sys, traceback
import os
import pendulum
from oppai import parser
from functions import beatmaps,printmsg,oppaiurl
import json
apikey='apikey'
client = discord.Client()
refreshtime = int(30)
#used for how long the database is to go back
pastDays=10

global enabled
enabled=[]
@client.event
async def bot_gamestatus():
    await client.wait_until_ready()
    await client.change_presence(game=discord.Game(name='Hosted on Heroku'))
    await client.edit_profile(username="Totally Functional Bot")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    #create a txt file that will be used on startup for enabled/disabled channels
    f = open("channels.txt","r+")
    contents=f.readlines()
    for x in range(len(contents)):
        enabled.append(client.get_channel(contents[x].strip('\n')))
    f.close()

@client.event
async def on_message(message):
    if message.content.startswith('^enable'):
        #only send updates on enabled channels
        if not message.channel in enabled:
            enabled.append(message.channel)
            await client.send_message(message.channel, 'Future messages will be displayed on this channel')
            #write to txt file
            f = open("channels.txt","a")
            f.write(message.channel.id+"\n")
            f.close()
        else:
             await client.send_message(message.channel, 'Future messages are already displayed on this channel')
    #remove from channel
    if message.content.startswith('^disable'):
        enabled.remove(message.channel)
        await client.send_message(message.channel, 'Future messages will no longer be displayed on this channel')
        #read from txt file
        f = open("channels.txt","r+")
        d = f.readlines()
        f.seek(0)
        for i in d:
            if i != message.channel.id+"\n":
                f.write(i)
        f.truncate()
        f.close()
    #used for testing
    if message.content.startswith('^b/'):
            req=await oppaiurl(client,message.content[3:])
            if req is None:
                await client.send_message(message.channel,"invalid string")
            else:
                x=parser(req)
                if type(x)==str:
                    await client.send_message(message.channel,x)
                else:
                    url="https://osu.ppy.sh/b/"+message.content[3:]
                            
                    em = discord.Embed()
                    em.title = "**:heart:" +"Latest Ranked**"
                    em.description= "**[%s - %s [%s] (by %s)](%s)**\n" "**CS%g OD%g AR%g HP%g**\n""**max combo: %dx %.3g★**\n""%.3gpp for %g%%\n""%.3gpp for %.2g%%\n""%.3gpp for %g%% with HDHR" %(x[0],x[1],x[2],x[3],url,x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12],x[13],x[14],x[15])
                    em.set_thumbnail(url='https://b.ppy.sh/thumb/554084l.jpg')
                  
                    await client.send_message(message.channel,embed=em)
    
        
        
        
@client.event
async def qualifiedtester():
    
    
    ranked=[]
    qualified=[]
    loopcounter=0
    beatmap=[]
    await client.wait_until_ready()
    while not client.is_closed:
        #dictionary of beatmaps ranked in last days
        time=pendulum.now().in_tz('Asia/Tokyo').subtract(days=pastDays).to_datetime_string()
        while True:
            update=await beatmaps(apikey,'&since='+time,'',)     
            if update is None:            
                 await asyncio.sleep(30)
                 update=await beatmaps(apikey,'&since='+time,'')
                 print("retrying")
            else:
                break

        #seperate beatmaps into either ranked/qualified-----------------------------------------
        for i in update:
           if i["approved"]=="1" or i["approved"]=="2" or i["approved"]=="4":
               #append only if the beatmap not already in the ranked list, if map has been ranked recently then remove from qualified list
               if not next((item for item in ranked if item["beatmapset_id"] == i["beatmapset_id"]),None):
                   ranked.append(i)
                   await printmsg(client,loopcounter,i,'Ranked',apikey,enabled)
                   if i in qualified:
                       qualified.remove(i)
           elif i["approved"]=="3":
                if not next((item for item in qualified if item["beatmapset_id"] == i["beatmapset_id"]),None):
                   qualified.append(i)
                   await printmsg(client,loopcounter,i,'Qualified',apikey,enabled)   
        for i in qualified:
            if  not any(i['beatmapset_id']==j['beatmapset_id'] for j in update) and any(i['beatmapset_id']==j['beatmapset_id'] for j in beatmap):
                await printmsg(client,loopcounter,i,'Disqualified',apikey,enabled)
                qualified.remove(i)
        #debug------------------------------------------------------------------------------------------------------------------      
        if len(beatmap) !=len(update):           
            print(str(len(beatmap))+'--'+str(len(update))+'--'+time)
        #-----------------------------------------------------------------------------------------------------------------------
        beatmap=update
        loopcounter+=1
        await asyncio.sleep(refreshtime)


    


client.loop.create_task(qualifiedtester())
client.loop.create_task(bot_gamestatus())
client.run('token')



