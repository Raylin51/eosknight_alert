const axios = require('axios');

// 账号参数
const sckey = '';
const account = 'linzhanjie51';

// 拉表格
const getTableData = async table => {
    return new Promise((resolve, reject) => {
        const encodedName = getEncodeAccount(account);
        const url = 'https://api.eosnewyork.io/v1/chain/get_table_rows';
        const data = {
            json: true,
            code: 'eosknightsio',
            scope: 'eosknightsio',
            table: table,
            table_key: '',
            key_type: 'i64',
            lower_bound: encodedName,
            index_position: 1,
            limit: 1
        };
        const headers = {
            'content-type': 'application/json; charset=UTF-8'
        }
        axios({
            method: 'POST',
            url: url,
            headers: headers,
            data: data,
            responseType: 'json'
        }).then((r) => {
            const responseData = r.data.rows[0];
            resolve(responseData);
        }).catch((error) => {
            if (error.response) {
                console.log(error.response.data);
                reject(error);
            }
        });
    });
}

// 算杀人数，目前没用到
function calcKillCount(defense, hp, attack, time = 864000000000) {
    let damage_per_min = 25 - (25 * defense) / (defense + 1000);
    let alive_sec = (60 * hp) / damage_per_min;
    if (time < alive_sec) {
        alive_sec = time;
    }
    let current_kill_count = (attack * alive_sec) / (60 * 200);
    return current_kill_count;
}

function calcKillAliveTime(defense, hp) {
    let damage_per_min = 25 - (25 * defense) / (defense + 1000);
    let alive_sec = (60 * hp) / damage_per_min;
    return alive_sec;
}

// 计算最大时间
async function getKnightsMaxTime() {
    const dataObj = await getTableData('knight');
    const knights = ['knight', 'archer', 'mage'];
    const knightsObj = {};
    knights.map((role, index) => {
        index +=1 ;
        const obj = dataObj['rows'].find(function(x) {
            return x.type === index;
        });
        knightsObj[`${role}Obj`] = obj;
    });
    const knightMaxTime = calcKillAliveTime(knightsObj.knightObj.defense, knightsObj.knightObj.hp);
    const archerMaxTime = calcKillAliveTime(knightsObj.archerObj.defense, knightsObj.archerObj.hp);
    const mageMaxTime = calcKillAliveTime(knightsObj.mageObj.defense, knightsObj.mageObj.hp);
    return Math.max(knightMaxTime, archerMaxTime, mageMaxTime);
    // console.log(Math.max(knightMaxTime, archerMaxTime, mageMaxTime));
}

// 获取当前时间
async function getKnightsCurrTime() {
    const dataObj = await getTableData('player');
    const lastRebirthTime = dataObj.last_rebirth;
    const currTime = Date.now() / 1000 - 1500000000 - lastRebirthTime;
    return currTime;
}

// 判断宠物远征
async function checkPetExpedition() {
    const dataObj = await getTableData('petexp');
    const pets = dataObj.rows;
    const currTime = Date.now() / 1000 - 1500000000;
    pets.map((pet, index) => {
        if (pet.isback === 0 && currTime >= pet.end && currTime - pet.end < 600) {
            msg = '宠物远征结束啦';
        }
    });
    if (msg === '') {
        console.log('好像没有远征结束的');
    }
}

// 判断能否复活
async function checkRebirth() {
    let maxTime, currTime;
    await getKnightsMaxTime().then(res => {maxTime = res});
    await getKnightsCurrTime().then(res => {currTime = res});
    if (currTime >= maxTime && currTime - maxTime < 600) {
        msg = '可以复活啦';
    } else {
        msg = '';
        console.log('好像没有可以复活的');
    }
}

// 获取字母序号
function getLetterNumber(letter) {
    const strMap = '.12345abcdefghijklmnopqrstuvwxyz';
    return strMap.indexOf(letter) * 16
}

// 获取账号的big number（天晓得这是啥）
function getEncodeAccount(account) {
    try {
        account = account.padStart(12, '.');
        let ret = 0;
        let reverseAccountArray = account.split('').reverse();
        reverseAccountArray.map((currentLetter, index) => {
            let letterNumber = getLetterNumber(currentLetter);
            ret = ret + Math.pow(32, index) * letterNumber;
        });
        return ret;
    }
    catch (e) {
        console.log(e);
        console.log('账号出错啦！');
    }
}

// 微信推送
function sendToWechat(msg) {
    let url = `https://sc.ftqq.com/${sckey}.send?text=${msg}`;
    axios({
        method: 'POST',
        url: url,
    }).then(() => {msg = ''});
}

// sleep
const sleep = (m) => {
    return new Promise((resolve, reject) => {
        setTimeout(resolve, 1000 * 60 * m);
    }).catch(e => reject(e));
}

async function checkAction() {
    try {
        let getHour = new Date().getUTCHours() + 8;
        if (getHour >= 1 && getHour <= 9 ) {
            checkTimeStep = 60;
        } else {
            await checkRebirth();
            if (msg !== '') {
                console.log(`消息：${msg}`);
                await sendToWechat(encodeURI(msg));
            }
            await sleep(1);
            await checkPetExpedition();
            if (msg !== '') {
                console.log(`消息：${msg}`);
                await sendToWechat(encodeURI(msg));
            }
        }
    }
    catch (e) {
        console.log(e);
        msg = '出错了！快看日志！';
        await sendToWechat(encodeURI(msg));
    }
}

let msg = '';
checkAction()
setInterval(() => {checkAction()}, 1000 * 60 * 5);
// checkAction();
// sendToWechat(encodeURI('中文试试'));
