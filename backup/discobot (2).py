
import discord
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sys, traceback
import os
import timeit
client = discord.Client()
refreshtime = int(30)
#list of enabled channels
global enabled
enabled=[]
@client.event
async def bot_gamestatus():
    await client.wait_until_ready()
    await client.change_presence(game=discord.Game(name='Hosted on Heroku'))


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
        

@client.event
async def scraper():
    await client.wait_until_ready()
    beatmaps=[]
    qualified=[]
    ranked=[]
    disqualified=[]
   
    try:
        #loopcounter used to prevent qualified msgs being sent on first loop
        loopcounter=0
        while not client.is_closed:
            start = timeit.default_timer()
            async with aiohttp.request('GET', 'https://osu.ppy.sh/p/beatmaplist&s=4&r=11') as resp:
                assert resp.status == 200
                r=await resp.text()
            soup=BeautifulSoup(r,'lxml')     
            #create a list of beatmaps in xml that refreshes
            #loop from here for update
            update=[]
            
            x=0
            
            while(x<len(soup.find_all('div', class_='beatmap'))):
                update.append((soup.find_all('div', class_='beatmap'))[x])
            #follow map link and check if ranked/pending/qualified
            #needs a rewrite to use the osu!api
                p=update[x]
                req=""
                mapurl="https://osu.ppy.sh"+p.find_all('a', class_='title')[0].get('href')
                async with aiohttp.request('GET', mapurl) as resp:
                       assert resp.status == 200
                       req=await resp.text()

                soup2=BeautifulSoup(req,'lxml')
        
                #check if ranked/qualified/unqualified
                if soup2.find_all(id='songinfo')[0].find_all('tr')[6].text.find("Ranked")>=0:
                       artist = p.find_all('span', class_='artist')[0].text
                       title = p.find_all('a', class_='title')[0].text
                       mapper = p.find_all('div', class_='left-aligned')[0].find_next('a').text
                       mapid = p.find_all('a', class_='title')[0].get('href')
                       maplink = "https://osu.ppy.sh" + mapid
                       mapperid = p.find_all('div', class_='left-aligned')[0].find_next('a').get('href')
                       if mapid not in ranked:
                               ranked.append(mapid)
                               if loopcounter>=1:
                                   for i in range(len(enabled)):
                                           print("message sent in"+str(enabled[i]))
                                           await client.send_message(enabled[i],artist+"-"+title+" by "+mapper+" is now Ranked! "+maplink)
                       if mapid in qualified:
                           qualified.remove(mapid)
                       if mapid in disqualified:
                           disqualified.remove(mapid)
                                   
                elif soup2.find_all(id='songinfo')[0].find_all('tr')[6].text.find("Qualified")>=0:
                       artist = p.find_all('span', class_='artist')[0].text
                       title = p.find_all('a', class_='title')[0].text
                       mapper = p.find_all('div', class_='left-aligned')[0].find_next('a').text
                       mapid = p.find_all('a', class_='title')[0].get('href')
                       maplink = "https://osu.ppy.sh" + mapid
                       mapperid = p.find_all('div', class_='left-aligned')[0].find_next('a').get('href')
                       if mapid not in qualified:
                               qualified.append(mapid)
                               if loopcounter>=1:
                                   for i in range(len(enabled)):
                                                print("message sent in"+str(enabled[i]))
                                                await client.send_message(enabled[i],artist+"-"+title+" by "+mapper+" is now Qualified! "+maplink)
                       if mapid in ranked:
                           ranked.remove(mapid)
                       if mapid in disqualified:
                           disqualified.remove(mapid)
                else:
                       artist = p.find_all('span', class_='artist')[0].text
                       title = p.find_all('a', class_='title')[0].text
                       mapper = p.find_all('div', class_='left-aligned')[0].find_next('a').text
                       mapid = p.find_all('a', class_='title')[0].get('href')
                       maplink = "https://osu.ppy.sh" + mapid
                       mapperid = p.find_all('div', class_='left-aligned')[0].find_next('a').get('href')
                       if mapid not in disqualified:
                               disqualified.append(mapid)
                               if loopcounter>=1:
                                   for i in range(len(enabled)):
                                                print("message sent in"+str(enabled[i]))
                                                await client.send_message(enabled[i],artist+"-"+title+" by "+mapper+" is now Disqualified! "+maplink)
                       if mapid in ranked:
                           ranked.remove(mapid)
                       if mmapid in qualified:
                           qualified.remove(mapid)
                x+=1
           #loop end here for database update                          
            #check when a beatmap is missing from qualified section
            setUpdate=set(update)
            setBeatmaps=set(beatmaps)
            #check for missing beatmaps
            if beatmaps:
                missing=list((setUpdate)^(setBeatmaps))
                for i in range(len(missing)):
                    mapid=missing[i].find_all('a', class_='title')[0].get('href')
                    if missing[i] in ranked:
                        ranked.remove(missing[i])
                    elif missing[i] in qualified:
                        qualified.remove(missing[i])
                    elif missing[i] in disqualified:
                        
                        disqualified.remove(missing[i])
                        
            
            #update database
            loopcounter+=1
            beatmaps=list(update)
            stop = timeit.default_timer()
            print (stop - start )
    except: 
         traceback.print_exc(file=sys.stdout)
            
    await asyncio.sleep(refreshtime)
client.loop.create_task(bot_gamestatus())
client.loop.create_task(scraper())
client.run('MzA2NDA2MjU1MTc2NDUwMDYw.C-JtDA.OsvJr26ypsooUVJEN5GK2cUXZQo')



