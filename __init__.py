from email.headerregistry import Group
from typing import Tuple, Any
from string import Template
import requests
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata, on_regex
from nonebot.adapters.onebot.v11 import MessageSegment, ActionFailed, Bot, MessageEvent
from .VITS import Trans
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-atri",
    description="VITS 模型拟声",
    usage="AI声音\n" +
          "- 中日双语\n",
    extra={
        "unique_name": "gal_voice_bot",
        "example": "说お兄ちゃん大好き",
        "author": "Hitenmon <haominshan@gmail.com>",
        "version": "0.1.0",
    },
)

import os
# api for other plugins

model_dict = {'atri': 0, 'yuzu': 1}


def vits_func(msg, model, name=0):
    Trans(text=msg, model=model, speaker_id=name)
    voice = f'file:///'+os.getcwd()+'/voice.wav'
    return MessageSegment.record(voice)


yuzu_dict = {"宁宁": 0, "爱瑠": 1, "芳乃": 2, "茉子": 3, "丛雨": 4, "小春": 5, "七海": 6, }


cnapi = Template(
    "http://233366.proxy.nscc-gz.cn:8888?speaker=${id}&text=${text}")


def genshin_func(msg, name='派蒙'):
    voice = requests.get(cnapi.substitute(text=msg, id=name)).content
    return MessageSegment.record(voice)


Priority = 5

gp = True
send_id = 924579723
g_p_regex = "^(群聊|私聊)(.+)$"
g_p_cmd = on_regex(g_p_regex, block=True, priority=Priority)


def atoi(s):
    s = s[::-1]
    num = 0
    for i, v in enumerate(s):
        for j in range(0, 10):
            if v == str(j):
                num += j * (10 ** i)
    return num


@g_p_cmd.handle()
async def g_p_handler(event: MessageEvent, matched: Tuple[Any, ...] = RegexGroup()):
    g_p, id = matched[0], matched[1]
    user_id = event.get_user_id()
    if user_id not in Config.superusers:
        await g_p_cmd.finish('权限不足')
    global gp
    global send_id
    send_id = atoi(id)
    if (g_p == '群聊'):
        gp = True
        # print("切换至群聊对象{0}".format(send_id))
        await g_p_cmd.finish("切换至群聊对象{0}".format(send_id))
    else:
        gp = False
        # print("切换至私聊对象{0}".format(send_id))
        await g_p_cmd.finish("切换至私聊对象{0}".format(send_id))

atri_regex = "^(亚托莉|ATRI|atri)(发送|说|\ )(.+)$"
yuzu_regex = "^(宁宁|爱瑠|芳乃|茉子|丛雨|小春|七海)(发送|说|\ )(.+)$"
genshin_chars = '派蒙|凯亚|安柏|丽莎|琴|香菱|枫原万叶|迪卢克|温迪|可莉|早柚|托马|芭芭拉|优菈|云堇|钟离|魈|凝光|雷电将军|北斗|甘雨|七七|刻晴|神里绫华|雷泽|神里绫人|罗莎莉亚|阿贝多|八重神子|宵宫|荒泷一斗|九条裟罗|夜兰|珊瑚宫心海|五郎|达达利亚|莫娜|班尼特|申鹤|行秋|烟绯|久岐忍|辛焱|砂糖|胡桃|重云|菲谢尔|诺艾尔|迪奥娜|鹿野院平藏'
genshin_regex = "^({0})(发送|说|\ )(.+)$".format(genshin_chars)

atri_cmd = on_regex(atri_regex, block=True, priority=Priority)
genshin_cmd = on_regex(genshin_regex, block=True, priority=Priority)
yuzu_cmd = on_regex(yuzu_regex, block=True, priority=Priority)


async def cmd_handler(voice_msg, bot: Bot, event: MessageEvent):
    try:
        if (gp):
            await bot.send(event=event, message=voice_msg)
        else:
            await bot.send(event=event, message=voice_msg)
    except ActionFailed as e:
        await bot.send(event=event, message='API调用失败：' + str(e) + '。请检查输入字符是否匹配语言。')


async def remote_cmd_handler(voice_msg, bot: Bot, event: MessageEvent):
    user_id = event.get_user_id()
    if user_id not in Config.superusers:
        await bot.send('权限不足')
    try:
        if (gp):
            await bot.send_group_msg(group_id=send_id, message=voice_msg)
        else:
            await bot.send_private_msg(user_id=send_id, message=voice_msg)
        await atri_cmd.finish('发送成功')
    except ActionFailed as e:
        await atri_cmd.finish('API调用失败：' + str(e) + '。请检查输入字符是否匹配语言。')


@atri_cmd.handle()
async def atri_handler(bot: Bot, event: MessageEvent, matched: Tuple[Any, ...] = RegexGroup()):
    name, msg = matched[0], matched[2]
    print('语音发送中：atri {0} {1}'.format(name, msg))
    await cmd_handler(voice_msg=vits_func(msg, model_dict['atri'], 0), bot=bot, event=event)
    await atri_cmd.finish()


@yuzu_cmd.handle()
async def yuzu_handler(bot: Bot, event: MessageEvent, matched: Tuple[Any, ...] = RegexGroup()):
    name, msg = matched[0], matched[2]
    print('语音发送中：yuzu {0} {1}'.format(name, msg))
    await cmd_handler(voice_msg=vits_func(msg, model_dict['yuzu'], yuzu_dict[name]), bot=bot, event=event)
    await yuzu_cmd.finish()


@genshin_cmd.handle()
async def genshin_handler(bot: Bot, event: MessageEvent, matched: Tuple[Any, ...] = RegexGroup()):
    name, msg = matched[0], matched[2]
    print('语音发送中：genshin {0} {1}'.format(name, msg))
    await cmd_handler(voice_msg=genshin_func(msg, name), bot=bot, event=event)
    await genshin_cmd.finish()
