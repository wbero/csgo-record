import requests
import re
import html2text
from json import load, dump
from os.path import dirname, join, exists
import json
import math
import js2xml
from bs4 import BeautifulSoup
import numpy as np
from nonebot import get_bot
from hoshino.typing import NoticeSession
from asyncio import Lock, get_event_loop, run_coroutine_threadsafe
from hoshino import Service, priv
from os.path import dirname, join, exists
from hoshino.typing import CQEvent, MessageSegment as ms
from threading import Lock
from copy import deepcopy

sv_help = '''[官匹绑定 steamid] 绑定官匹steamid
[官匹查询 steamid] 查询官匹简要信息,绑定后不需要steamid'''

sv = Service('_csgo_', manage_priv=priv.SUPERUSER, visible=False)


curpath = dirname(__file__)
config = join(curpath, 'binds.json')
root = {
    'arena_bind' : {}
}

lck = Lock()

if exists(config):
    with open(config) as fp:
        root = load(fp)
binds = root['arena_bind']

def arena_miner(id):
	print(f'steamid为{id}')
	id = int(id)
	api_url = 'https://api.wmpvp.com/api/v2/csgo/detailStats'
	data = {"steamId64": f"{id}"}
	print(data)
	headers = {'content-type': "application/json"}
	response = requests.post(api_url, data = json.dumps(data), headers = headers)
	htmlurl2 = response.text
	soup= BeautifulSoup(htmlurl2, 'html.parser')
	data2 = soup.text
	historyWinCount = re.findall('\d+', str(re.findall('"historyWinCount":\d+', data2)))[0]
	cnt = re.findall('\d+', str(re.findall('"cnt":\d+', data2)))[0]
	kd = re.findall('(\d+(\.\d+)?)', str(re.findall('"kd":[\d+\.\d+]*', data2)[0]))[0][0]
	winRate = re.findall('(\d+(\.\d+)?)', str(re.findall('"winRate":[\d+\.\d+]*', data2)[0]))[0][0]
	winRate = str(float(winRate)*100)+'%'
	rating = re.findall('(\d+(\.\d+)?)', str(re.findall('"rating":[\d+\.\d+]*', data2)[0]))[0][0]

	kills = re.findall('\d+', str(re.findall('"kills":\d+', data2)))[0]
	deaths = re.findall('\d+', str(re.findall('"deaths":\d+', data2)))[0]
	assists = re.findall('\d+', str(re.findall('"assists":\d+', data2)))[0]
	rws = re.findall('(\d+(\.\d+)?)', str(re.findall('"rws":[\d+\.\d+]*', data2)[0]))[0][0]
	adr = re.findall('(\d+(\.\d+)?)', str(re.findall('"adr":[\d+\.\d+]*', data2)[0]))[0][0]
	kast = re.findall('\d+', str(re.findall('"kast":\d+', data2)))[0]
	k3 = re.findall('\d+', str(re.findall('"k3":\d+', data2)))[1]
	k4 = re.findall('\d+', str(re.findall('"k4":\d+', data2)))[1]
	k5 = re.findall('\d+', str(re.findall('"k5":\d+', data2)))[1]
	vs3 = re.findall('\d+', str(re.findall('"vs3":\d+', data2)))[1]
	vs4 = re.findall('\d+', str(re.findall('"vs4":\d+', data2)))[1]
	vs5 = re.findall('\d+', str(re.findall('"vs5":\d+', data2)))[1]
	headShotRatio = re.findall('(\d+(\.\d+)?)', str(re.findall('"headShotRatio":[\d+\.\d+]*', data2)[0]))[0][0]
	entryKillRatio = re.findall('(\d+(\.\d+)?)', str(re.findall('"entryKillRatio":[\d+\.\d+]*', data2)[0]))[0][0]
	awpKillRatio = re.findall('(\d+(\.\d+)?)', str(re.findall('"awpKillRatio":[\d+\.\d+]*', data2)[0]))[0][0]
	flashSuccessRatio = re.findall('(\d+(\.\d+)?)', str(re.findall('"flashSuccessRatio":[\d+\.\d+]*', data2)[0]))[0][0]

	msg = f'{id}的战绩如下：\n历史胜场为{historyWinCount},\n官匹场次为{cnt},\nK/D为{kd},\n胜率为{winRate},\nRating为{rating},\n杀敌数为{kills},\n助攻数为{assists},\n死亡为{deaths},\nRW为{rws},\n三杀次数为{k3},\n四杀次数为{k4},\n五杀次数为{k5},\n1v3次数为{vs3},\n1v4次数为{vs4},\n1v5次数为{vs5},\n爆头率为{headShotRatio},\n首杀率为{entryKillRatio},\nAWP击杀率为{awpKillRatio},\n闪白成功率为{flashSuccessRatio}'
	print(msg)
	return msg


def save_binds():
    with open(config, 'w') as fp:
        dump(root, fp, indent=4)

@sv.on_rex(r'^官匹绑定 ?(\d{17})$')
async def on_arena_bind(bot, ev):
    global binds, lck

    with lck:
        uid = str(ev['user_id'])
        last = binds[uid] if uid in binds else None

        binds[uid] = {
            'id': ev['match'].group(1),
            'uid': uid,
            'gid': str(ev['group_id']),
        }
        save_binds()

    await bot.finish(ev, '官匹绑定成功', at_sender=True)

@sv.on_rex(r'^官匹查询 ?(\d{17})?$')
async def on_query_arena(bot, ev):
    global binds, lck

    robj = ev['match']
    id = robj.group(1)
    if id == None:
        uid = str(ev['user_id'])
        print(binds)
        if not uid in binds:
            await bot.finish(ev, '您还未绑定官匹steamid', at_sender=True)
            return
        else:
            id = binds[uid]['id']
    try:
        res = arena_miner(id)
        await bot.send(ev, res)
    except Exception as e: 
        await bot.finish(ev, f'查询出错{e}', at_sender=True)












