import discord
import asyncio
import urllib.request
from bs4 import BeautifulSoup
import sys, traceback

client = discord.Client()
refreshtime = int(30)
#list of enabled channels
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

@client.event
async def on_message(message):
    if message.content.startswith('^enable'):
        #only send updates on enabled channels
        if not message.channel in enabled:
            enabled.append(message.channel)
            await client.send_message(message.channel, 'Future messages will be displayed on this channel')
        else:
             await client.send_message(message.channel, 'Future messages are already displayed on this channel')
    #remove from channel
    if message.content.startswith('^disable'):
        enabled.remove(message.channel)
        await client.send_message(message.channel, 'Future messages will no longer be displayed on this channel')
        

@client.event
async def scraper():
    await client.wait_until_ready()
    beatmaps=[]
    qualified=[]
    ranked=[]
    disqualified=[]
    r=urllib.request.urlopen('https://osu.ppy.sh/p/beatmaplist&s=4&r=11').read()
    soup=BeautifulSoup(r,'lxml')
    loopcounter=0
    while not client.is_closed:

#loop through qualified page
#visit every link
#check BSobject if its ranked/qualified/pending 
#if newly qualified/ranked/pending, display message
    #add to qualified/ranked/pending database
#check for missing beatmaps off of qualified
#if missing remove from message displayed database
#update database

        try:
           
            #create a list of beatmaps in xml that refreshes
            #loop from here for update
            update=[]
            print("current loop counter: "+str(loopcounter))
            
            x=0
            while(x<len(soup.find_all('div', class_='beatmap'))):
                update.append((soup.find_all('div', class_='beatmap'))[x])
                print("did it enter here")
            #follow map link and check if ranked/pending/qualified   
            #loop only if there is previous database            
                if beatmaps:
                   p=update[x]
                   mapurl="https://osu.ppy.sh"+p.find_all('a', class_='title')[0].get('href')
                   req=urllib.request.urlopen(mapurl).read()
                   soup2=BeautifulSoup(req,'lxml')

                   #check if ranked/qualified/unqualified
                   if soup2.find_all(id='songinfo')[0].find_all('tr')[6].text.find("Ranked")>=0:
                       artist = p.find_all('span', class_='artist')[0].text
                       title = p.find_all('a', class_='title')[0].text
                       mapper = p.find_all('div', class_='left-aligned')[0].find_next('a').text
                       mapid = p.find_all('a', class_='title')[0].get('href')
                       maplink = "https://osu.ppy.sh" + mapid
                       mapperid = p.find_all('div', class_='left-aligned')[0].find_next('a').get('href')
                       if p not in ranked:
                           ranked.append(p)
                           for i in range(len(enabled)):
                               print("message sent in"+enabled[i])
                               await client.send_message(enabled[i],artist+"-"+title+" by "+mapper+" is now Ranked! "+maplink)
                           
                   elif soup2.find_all(id='songinfo')[0].find_all('tr')[6].text.find("Qualified")>=0:
                       artist = p.find_all('span', class_='artist')[0].text
                       title = p.find_all('a', class_='title')[0].text
                       mapper = p.find_all('div', class_='left-aligned')[0].find_next('a').text
                       mapid = p.find_all('a', class_='title')[0].get('href')
                       maplink = "https://osu.ppy.sh" + mapid
                       mapperid = p.find_all('div', class_='left-aligned')[0].find_next('a').get('href')
                       if p not in qualified:
                           qualified.append(p)
                           for i in range(len(enabled)):
                                print("message sent in"+enabled[i])
                                await client.send_message(enabled[i],artist+"-"+title+" by "+mapper+" is now Qualified! "+maplink)
                   else:
                       artist = p.find_all('span', class_='artist')[0].text
                       title = p.find_all('a', class_='title')[0].text
                       mapper = p.find_all('div', class_='left-aligned')[0].find_next('a').text
                       mapid = p.find_all('a', class_='title')[0].get('href')
                       maplink = "https://osu.ppy.sh" + mapid
                       mapperid = p.find_all('div', class_='left-aligned')[0].find_next('a').get('href')
                       if p not in disqualified:
                           disqualified.append(p)
                       for i in range(len(enabled)):
                            print("message sent in"+enabled[i])
                            await client.send_message(enabled[i],artist+"-"+title+" by "+mapper+" is now Disqualified! "+maplink)
           
                x+=1


           #loop end here for database update                          
            #check when a beatmap is missing from qualified
            setUpdate=set(update)
            setBeatmaps=set(beatmaps)
            #check for missing beatmaps
            if beatmaps:
                missing=list((setUpdate)^(setBeatmaps))
                for i in range(len(missing)):
                    if missing[i] in ranked:
                        ranked.remove(missing[i])
                    elif missing[i] in qualified:
                        qualified.remove(missing[i])
                    else :
                        disqualified.remove(missing[i])
            
            #update database

            beatmaps=list(update)
        except: 
            traceback.print_exc(file=sys.stdout)
            
        loopcounter+=1
        await asyncio.sleep(refreshtime)
client.loop.create_task(bot_gamestatus())
client.loop.create_task(scraper())
client.run('MzA2NDA2MjU1MTc2NDUwMDYw.C-JtDA.OsvJr26ypsooUVJEN5GK2cUXZQo')



