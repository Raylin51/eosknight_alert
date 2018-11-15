#!/usr/bin/env python
# coding: utf-8

from __future__ import division
import urllib
import requests
import json
import time
import sys

# 计算击杀数
def calcKillCount(defense, hp, attack, time = 864000000000):
    damage_per_min = 25 - (25 * defense) / (defense + 1000)
    alive_sec = (60 * hp) / damage_per_min
    if time < alive_sec:
        alive_sec = time
    current_kill_count = (attack * alive_sec) / (60 * 200)
    return current_kill_count


# 计算存活时间
def calcKillAliveTime(defense, hp):
    damage_per_min = 25 - (25 * defense) / (defense + 1000)
    alive_sec = (60 * hp) / damage_per_min
    return alive_sec


# 计算多个骑士最大存活时间
def getKnightsMaxTime(encodedName):
    url = 'https://api.eosnewyork.io/v1/chain/get_table_rows'

    data_json = {'json': True, 'code': 'eosknightsio', 'scope': 'eosknightsio', 'table': 'knight', 'table_key': '',
                 'key_type': 'i64', 'lower_bound': encodedName, 'index_position': 1, 'limit': 1}

    headers = {'content-type': 'application/json; charset=UTF-8'}
    data = json.dumps(data_json, ensure_ascii=False).encode('utf8')
    try:
        r = requests.post(url, data=data, headers=headers)
        ans = r.json()['rows'][0]
        t1 = calcKillAliveTime(ans['rows'][0]['defense'], ans['rows'][0]['hp'])
        t2 = calcKillAliveTime(ans['rows'][1]['defense'], ans['rows'][1]['hp'])
        t3 = calcKillAliveTime(ans['rows'][2]['defense'], ans['rows'][2]['hp'])
        return max(t1, t2, t3)

    except Exception, e:
        print Exception, ":", e
        return 0


# 获取骑士当前时间
def getKnightsCurrTime(encodedName):
    url = 'https://api.eosnewyork.io/v1/chain/get_table_rows'

    data_json = {'json': True, 'code': 'eosknightsio', 'scope': 'eosknightsio', 'table': 'player', 'table_key': '',
                 'key_type': 'i64', 'lower_bound': encodedName, 'index_position': 1, 'limit': 1}

    headers = {'content-type': 'application/json; charset=UTF-8'}
    data = json.dumps(data_json, ensure_ascii=False).encode('utf8')
    try:
        r = requests.post(url, data=data, headers=headers)
        ans = r.json()['rows'][0]['last_rebirth']
        return int(time.time()) - 1500000000 - ans
    except Exception, e:
        print Exception, ":", e
        return 0


# 获取宠物远征是否可以回来
def getPetExpedition(account, encodedName):
    url = 'https://api.eosnewyork.io/v1/chain/get_table_rows'

    data_json = {'json': True, 'code': 'eosknightsio', 'scope': 'eosknightsio', 'table': 'petexp', 'table_key': '',
                 'key_type': 'i64', 'lower_bound': encodedName, 'index_position': 1, 'limit': 1}

    headers = {'content-type': 'application/json; charset=UTF-8'}
    data = json.dumps(data_json, ensure_ascii=False).encode('utf8')
    try:
        r = requests.post(url, data=data, headers=headers)
        pets = r.json()['rows'][0]['rows']
        # print pets
        curr = int(time.time()) - 1500000000
        for pet in pets:
            if pet['isback'] == 0:  # 处于远征状态
                # print curr,pet['end']
                if curr >= pet['end'] and curr - pet['end'] < 600:  # 可以回来了
                    print '%s 宠物远征结束了' % account
                    return '%s 宠物远征结束了' % account

        return ''
    except Exception, e:
        print Exception, ":", e
        return ''


# 微信推送消息
def sendToWechat(sckey, msg):
    url = 'https://sc.ftqq.com/%s.send?text=%s' % (
        sckey, urllib.quote(msg))
    r = requests.get(url)


# 检查是否该复活了
def checkKnight(account, encodedName):
    maxTime = getKnightsMaxTime(encodedName)
    currTime = getKnightsCurrTime(encodedName)
    print "maxtime,currTime", maxTime, currTime
    if currTime >= maxTime and currTime - maxTime < 600:
        global checkTime
        checkTime = 30
        return '%s 该复活啦~\n' % (account)
    else:
        global checkTime
        checkTime = 5
        return ''


# 获取字母的序号
def getLetterNumber(letter):
    strMap = ".12345abcdefghijklmnopqrstuvwxyz"
    # .=>0*16
    # 1=>1*16
    # 2=>2*32
    # a=>6*16
    # z=>31*16
    return strMap.index(letter) * 16


# 获取账号的big number
def getEncodedAccount(account):
    try:
        account = account.rjust(12, '.')
        ret = 0
        index = 0
        # ascii 49=>1  53=>5  97=>a  122=>z
        for letter in reversed(account):
            int = getLetterNumber(letter)
            ret = ret + pow(32, index) * int
            index = index + 1
        return ret
    except:
        print "账号出错！请检查账号！"
        sys.exit(1)


if __name__ == '__main__':
    global checkTime
    checkTime = 5
    ################################################
    sckey = ''  # 你的key
    accounts = {
        'linzhanjie51'
    }
    ################################################
    encodedAccounts = {}
    for account in accounts:
        encodedAccounts[account] = getEncodedAccount(account)
    # print encodedAccounts

    while True:
        try:
            str = ''
            for acc in accounts:
                encAcc = encodedAccounts[acc]
                # print acc,encAcc
                str += checkKnight(acc, encAcc)
                str += getPetExpedition(acc, encAcc)
            print str
            if len(str) > 12:
                sendToWechat(sckey, str)
            print '========' + time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())) + '============'
            time.sleep(60 * checkTime)  # 每5分钟循环一次
        except Exception as e:
            print "有错误！！", e
            time.sleep(20)  # 如果发生错误，延迟20秒再次执行
