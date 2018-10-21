import discord
import asyncio
import aiohttp
import re
from oppai import parser
import sys, traceback
import json

#given beatmap id format url for oppai
async def oppaiurl(client,url):
    url="https://osu.ppy.sh/osu/"+url
    async with aiohttp.request('GET', url) as r:
        req=await r.text()
        if not req:
                return None
        return req
        
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




             
#display a message map given beatmap and its ranked status
async def printmsg(client,loopcounter,beatmap,status,apikey,enabled):
    if loopcounter>=1:
        print(beatmap['artist']+'-'+beatmap['title']+" is now "+status)
        req=''
        url='https://osu.ppy.sh/api/get_beatmaps?k='+apikey+'&b='+beatmap['beatmap_id']
        print(url)
        async with aiohttp.request('GET', url) as r:
            req=await r.text()
            if not req:
                for i in range(len(enabled)):
                    await client.send_message(enabled[i], beatmap['artist']+'-'+beatmap['title']+" is now "+status+'\ninvalid string')
            url2=await oppaiurl(client,beatmap['beatmap_id'])
            x=parser(url2)
            
            for i in range(len(enabled)):
                icon=""
                if status=="Ranked":
                    icon=':heart:'
                elif status=="Qualified":
                    icon=':ballot_box_with_check:'
                else:
                    icon=':broken_heart:'
                url="https://osu.ppy.sh/b/"+beatmap['beatmap_id']
                        
                em = discord.Embed()
                em.title = "**"+icon +"Latest" +status+"**"
                if type(x)==str:
                    em.description= "**[%s - %s [%s] (by %s)](%s)**\n" "%s" %(x[0],x[1],x[2],x[3],url,x)
                else:
                    em.description= "**[%s - %s [%s] (by %s)](%s)**\n" "**CS%g OD%g AR%g HP%g**\n""**max combo: %dx %.3g★**\n""%.3gpp for %g%%\n""%.3gpp for %.2g%%\n""%.3gpp for %g%% with HDHR" %(x[0],x[1],x[2],x[3],url,x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12],x[13],x[14],x[15])
                em.set_thumbnail(url='https://b.ppy.sh/thumb/'+beatmap['beatmapset_id']+'l.jpg')
                await client.send_message(enabled[i],embed=em)




