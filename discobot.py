import discord
import asyncio
import aiohttp
import sys, traceback
import os
import pendulum
import re
import json
from oppai import parser
apikey='c822e841c28e578df4a621ed8820771212c62219'
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
    if message.content.startswith('^b/'):
        req=''
        url="https://osu.ppy.sh/osu/"+message.content[3:]
        async with aiohttp.request('GET', url) as r:
            req=await r.text()
            if not req:
                await client.send_message(message.channel, 'invalid string')

            x=parser(req)
            if type(x)==str:
                await client.send_message(message.channel,x)
            else:
                await client.send_message(message.channel,
                        "%s - %s [%s] (by %s)\n"
                        "CS%g OD%g AR%g HP%g\n"
                        "max combo: %d\n"
                        "stars: %.3g\n"
                        "%.3gpp for %g%%\n"
                        "%.3gpp for %.2g%%\n"
                        "%.3gpp for %g with HDHR" %
                        (x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12],x[13],x[14],x[15]))   
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
        #seperate beatmaps into either ranked/qualified
        for i in update:
           if i["approved"]=="1" or i["approved"]=="2" or i["approved"]=="4":
               #append only if the beatmap not already in the ranked list, if map has been ranked recently then remove from qualified list
               if not next((item for item in ranked if item["beatmapset_id"] == i["beatmapset_id"]),None):
                   ranked.append(i)
                   await printmsg(loopcounter,i,'ranked!')
                   if i in qualified:
                       qualified.remove(i)
           elif i["approved"]=="3":
                if not next((item for item in qualified if item["beatmapset_id"] == i["beatmapset_id"]),None):
                   qualified.append(i)
                   await printmsg(loopcounter,i,'qualified!')   
        for i in qualified:
            if i['beatmapset_id'] not in update and i['beatmapset_id'] in beatmap:
                await printmsg(loopcounter,i,'disqualified!')
                qualified.remove(i)
        if len(beatmap) !=len(update):           
            print(str(len(beatmap))+'--'+str(len(update))+'--'+time)
        beatmap=update
        loopcounter+=1
        await asyncio.sleep(refreshtime)


    
#creates a list of beatmaps given time
async def beatmaps(apikey,time,beatmapsetid):
    url = 'https://osu.ppy.sh/api/get_beatmaps?k='+apikey+time+beatmapsetid
    urltrim=re.sub('[\s+]', '', url)
    try:
        async with aiohttp.request('GET', urltrim) as r:
            req=await r.text()
            if type(req)!= None:
                return(json.loads(req))
            else:
                return None
    except Exception as e:
         traceback.print_exc(file=sys.stdout)
         return(None)
  #if map disappears from api then it has been disqualified               
      
async def printmsg(loopcounter,beatmap,status):
    if loopcounter>=1:
        print(beatmap['artist']+'-'+beatmap['title']+" is now "+status)
        req=''
        url='https://osu.ppy.sh/api/get_beatmaps?k='+apikey+'b='+beatmap['beatmap_id']
        async with aiohttp.request('GET', url) as r:
            req=await r.text()
            if not req:
                await client.send_message(message.channel, 'invalid string')

            x=parser(req)
            if type(x)==str:
                await client.send_message(message.channel,x)
            else:
                await client.send_message(message.channel,
                                         
                        "%s - %s [%s] (by %s) is now %s\n"
                        "CS%g OD%g AR%g HP%g\n"
                        "max combo: %d\n"
                        "stars: %.3g\n"
                        "%.3g pp for %g%%\n"
                        "%.3g pp for %.2g%%\n"
                        "%.3g pp for %g%% with HDHR" %
                        (x[0],x[1],x[2],x[3],status,x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12],x[13],x[14],x[15]))

client.loop.create_task(qualifiedtester())
client.loop.create_task(bot_gamestatus())
client.run('MzA2NDA2MjU1MTc2NDUwMDYw.C-JtDA.OsvJr26ypsooUVJEN5GK2cUXZQo')



