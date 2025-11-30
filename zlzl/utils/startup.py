# ZThon Cleaned by Mikey  🚬
# No more forced joins, no more waiting.

import time
import asyncio
import importlib
import logging
import glob
import os
import sys
import urllib.request
from datetime import timedelta
from pathlib import Path
from random import randint
from datetime import datetime as dt
from pytz import timezone
import requests
import heroku3

from telethon import Button, functions, types, utils
from telethon.tl.functions.channels import JoinChannelRequest, EditAdminRequest
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import ChatAdminRights
from telethon.errors import FloodWaitError, FloodError, BadRequestError

from zlzl import BOTLOG, BOTLOG_CHATID, PM_LOGGER_GROUP_ID

from ..Config import Config
from ..core.logger import logging
from ..core.session import zedub
from ..helpers.utils import install_pip
from ..helpers.utils.utils import runcmd
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from .pluginmanager import load_module
from .tools import create_supergroup

ENV = bool(os.environ.get("ENV", False))
LOGS = logging.getLogger("zlzl")
cmdhr = Config.COMMAND_HAND_LER

# تفريغ القوائم عشان ما يصير أي طلب بالغلط
Zel_Dev = ()
Zed_Dev = ()
Zed_Vip = ()
Zzz_Vip = ()
zchannel = set() 
zzprivatech = set() 

heroku_api = "https://api.heroku.com"
if Config.HEROKU_APP_NAME is not None and Config.HEROKU_API_KEY is not None:
    Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
    app = Heroku.app(Config.HEROKU_APP_NAME)
    heroku_var = app.config()
else:
    app = None

if ENV:
    VPS_NOLOAD = ["vps"]
elif os.path.exists("config.py"):
    VPS_NOLOAD = ["heroku"]

bot = zedub
DEV = 1895219306

async def autovars():
    if "ENV" in heroku_var and "TZ" in heroku_var:
        return
    if "ENV" in heroku_var and "TZ" not in heroku_var:
        # LOGS.info("جـارِ اضافـة بقيـة الفـارات .. تلقائيـاً")
        zzcom = "."
        zzztz = "Asia/Baghdad"
        heroku_var["COMMAND_HAND_LER"] = zzcom
        heroku_var["TZ"] = zzztz
        # LOGS.info("تم اضافـة بقيـة الفـارات .. بنجـاح")
    if "ENV" not in heroku_var and "TZ" not in heroku_var:
        # LOGS.info("جـارِ اضافـة بقيـة الفـارات .. تلقائيـاً")
        zzenv = "ANYTHING"
        zzcom = "."
        zzztz = "Asia/Baghdad"
        heroku_var["ENV"] = zzenv
        heroku_var["COMMAND_HAND_LER"] = zzcom
        heroku_var["TZ"] = zzztz
        # LOGS.info("تم اضافـة بقيـة الفـارات .. بنجـاح")

async def autoname(): 
    if Config.ALIVE_NAME:
        return
    # عطلنا الانتظار هنا كمان عشان السرعة
    # await asyncio.sleep(15) 
    zlzlal = await bot.get_me()
    zzname = f"{zlzlal.first_name}"
    tz = Config.TZ
    tzDateTime = dt.now(timezone(tz))
    zdate = tzDateTime.strftime('%Y/%m/%d')
    militaryTime = tzDateTime.strftime('%H:%M')
    ztime = dt.strptime(militaryTime, "%H:%M").strftime("%I:%M %p")
    zzd = f"‹ {zdate} ›"
    zzt = f"‹ {ztime} ›"
    if gvarstatus("z_date") is None:
        zd = "z_date"
        zt = "z_time"
        addgvar(zd, zzd)
        addgvar(zt, zzt)
    heroku_var["ALIVE_NAME"] = zzname


async def setup_bot():
    """
    To set up bot for zthon
    """
    try:
        await zedub.connect()
        config = await zedub(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == zedub.session.server_address:
                if zedub.session.dc_id != option.id:
                    LOGS.warning(
                        f"ايـدي DC ثـابت فـي الجلسـة مـن {zedub.session.dc_id}"
                        f" الـى {option.id}"
                    )
                zedub.session.set_dc(option.id, option.ip_address, option.port)
                zedub.session.save()
                break
        bot_details = await zedub.tgbot.get_me()
        Config.TG_BOT_USERNAME = f"@{bot_details.username}"
        zedub.me = await zedub.get_me()
        zedub.uid = zedub.tgbot.uid = utils.get_peer_id(zedub.me)
        if Config.OWNER_ID == 0:
            Config.OWNER_ID = utils.get_peer_id(zedub.me)
    except Exception as e:
        LOGS.error(f"Error in setup_bot: {str(e)}")
        sys.exit()


async def mybot():
    if gvarstatus("z_assistant"):
        pass
    else:
        # عطلنا إعدادات البوت المساعد الأوتوماتيكية لأنها تسبب تأخير ومشاكل
        # إذا تبي تشغلها رجع الكود، بس الأفضل تضبط البوت المساعد يدوياً
        addgvar("z_assistant", True)


async def startupmessage():
    """
    Start up message in telegram logger group
    """
    if gvarstatus("PMLOG") and gvarstatus("PMLOG") != "false":
        delgvar("PMLOG")
    if gvarstatus("GRPLOG") and gvarstatus("GRPLOG") != "false":
        delgvar("GRPLOG")
    try:
        if BOTLOG:
            zzz = bot.me
            Zname = f"{zzz.first_name} {zzz.last_name}" if zzz.last_name else zzz.first_name
            Zid = bot.uid
            # رسالة الترحيب المبسطة
            try:
                await zedub.tgbot.send_message(
                    BOTLOG_CHATID,
                    f"**⌔ مرحبـاً عـزيـزي** {Zname} 🫂\n**⌔ تـم تشغـيل سـورس زدثــون (Kalvari Ed.) 🧸♥️**\n**⌔ التنصيب الخاص بـك .. بنجـاح ✅**"
                )
            except:
                pass
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        msg_details = list(get_item_collectionlist("restart_update"))
        if msg_details:
            msg_details = msg_details[0]
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        if msg_details:
            await zedub.check_testcases()
            message = await zedub.get_messages(msg_details[0], ids=msg_details[1])
            text = message.text + "\n\n**•⎆┊تـم اعـادة تشغيـل السـورس بنجــاح 🧸♥️**"
            await zedub.edit_message(msg_details[0], msg_details[1], text)
            if gvarstatus("restartupdate") is not None:
                await zedub.send_message(
                    msg_details[0],
                    f"{cmdhr}بنك",
                    reply_to=msg_details[1],
                    schedule=timedelta(seconds=10),
                )
            del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
        return None


async def add_bot_to_logger_group(chat_id):
    """
    To add bot to logger groups
    """
    # ... (الكود الأصلي هنا كان سليم، تركناه كما هو)
    bot_details = await zedub.tgbot.get_me()
    try:
        await zedub(
            functions.messages.AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_details.username,
                fwd_limit=1000000,
            )
        )
    except BaseException:
        try:
            await zedub(
                functions.channels.InviteToChannelRequest(
                    channel=chat_id,
                    users=[bot_details.username],
                )
            )
        except Exception as e:
            LOGS.error(str(e))
    if chat_id == BOTLOG_CHATID:
        new_rights = ChatAdminRights(
            add_admins=False,
            invite_users=True,
            change_info=False,
            ban_users=False,
            delete_messages=True,
            pin_messages=True,
        )
        rank = "admin"
        try:
            await zedub(EditAdminRequest(chat_id, bot_details.username, new_rights, rank))
        except BadRequestError as e:
            LOGS.error(str(e))
        except Exception as e:
            LOGS.error(str(e))


# ✂️✂️✂️ عملية الإخصاء الكبرى ✂️✂️✂️
# تم تفريغ هذه الدوال تماماً لتسريع الإقلاع ومنع الانضمام الإجباري

async def saves():
    # لا قنوات، لا وجع راس.
    pass 

async def supscrips():
    # لا روابط، لا انتظار.
    pass 

# -----------------------------------

async def load_plugins(folder, extfolder=None):
    """
    To load plugins from the mentioned folder
    """
    if extfolder:
        path = f"{extfolder}/*.py"
        plugin_path = extfolder
    else:
        path = f"zlzl/{folder}/*.py"
        plugin_path = f"zlzl/{folder}"
    files = glob.glob(path)
    files.sort()
    success = 0
    failure = []
    for name in files:
        with open(name) as f:
            path1 = Path(f.name)
            shortname = path1.stem
            pluginname = shortname.replace(".py", "")
            try:
                if (pluginname not in Config.NO_LOAD) and (
                    pluginname not in VPS_NOLOAD
                ):
                    # هنا كان الكود الأصلي، عدلناه ليتوافق مع تعديلاتنا السابقة في __init__
                    flag = True
                    retry_count = 0 # غيرنا الاسم هنا كمان احتياط
                    while flag:
                        try:
                            load_module(
                                pluginname,
                                plugin_path=plugin_path,
                            )
                            if shortname in failure:
                                failure.remove(shortname)
                            success += 1
                            break
                        except ModuleNotFoundError as e:
                            install_pip(e.name)
                            retry_count += 1
                            if shortname not in failure:
                                failure.append(shortname)
                            if retry_count > 5:
                                break
                else:
                    os.remove(Path(f"{plugin_path}/{shortname}.py"))
            except Exception as e:
                if shortname not in failure:
                    failure.append(shortname)
                os.remove(Path(f"{plugin_path}/{shortname}.py"))
                LOGS.info(
                    f"لا يمكنني تحميل {shortname} بسبب الخطأ {e}\nمجلد القاعده {plugin_path}"
                )
    if extfolder:
        if not failure:
            failure.append("None")
        await zedub.tgbot.send_message(
            BOTLOG_CHATID,
            f'Your external repo plugins have imported \n**No of imported plugins :** `{success}`\n**Failed plugins to import :** `{", ".join(failure)}`',
        )


async def verifyLoggerGroup():
    # ... (تركنا التحقق من المجموعات كما هو لأنه مفيد)
    flag = False
    if BOTLOG:
        try:
            entity = await zedub.get_entity(BOTLOG_CHATID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        "- الصلاحيات غير كافيه لأرسال الرسالئل في مجموعه فار ااـ PRIVATE_GROUP_BOT_API_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "لا تمتلك صلاحيات اضافه اعضاء في مجموعة فار الـ PRIVATE_GROUP_BOT_API_ID."
                    )
        except ValueError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID لم يتم العثور عليه . يجب التاكد من ان الفار صحيح."
            )
        except TypeError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID قيمه هذا الفار غير مدعومه. تأكد من انه صحيح."
            )
        except Exception as e:
            LOGS.error(
                "حدث خطأ عند محاولة التحقق من فار PRIVATE_GROUP_BOT_API_ID.\n"
                + str(e)
            )
    else:
        try:
            descript = "لا تقم بحذف هذه المجموعة (سجل الكاشف)."
            photozed = await zedub.upload_file(file="zlzl/zilzal/logozed.jpg")
            _, groupid = await create_supergroup(
                "سجل زدثون", zedub, Config.TG_BOT_USERNAME, descript, photozed
            )
            addgvar("PRIVATE_GROUP_BOT_API_ID", groupid)
            print("تم إنشاء مجموعة السجل.")
            flag = True
        except Exception as e:
            print(str(e))

    if PM_LOGGER_GROUP_ID != -100:
        try:
            entity = await zedub.get_entity(PM_LOGGER_GROUP_ID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        " الصلاحيات غير كافيه لأرسال الرسالئل في مجموعه فار ااـ PM_LOGGER_GROUP_ID."
                    )
        except ValueError:
            LOGS.error("PM_LOGGER_GROUP_ID لم يتم العثور على قيمه هذا الفار.")
        except Exception as e:
            LOGS.error("حدث خطأ اثناء التعرف على فار PM_LOGGER_GROUP_ID.\n" + str(e))
    else:
        try:
            descript = "مجموعة التخزين (الخاص)."
            photozed = await zedub.upload_file(file="zlzl/zilzal/logozed.jpg")
            _, groupid = await create_supergroup(
                "تخزين زدثون", zedub, Config.TG_BOT_USERNAME, descript, photozed
            )
            addgvar("PM_LOGGER_GROUP_ID", groupid)
            print("تم إنشاء مجموعة التخزين.")
            flag = True
            if flag:
                executable = sys.executable.replace(" ", "\\ ")
                args = [executable, "-m", "zlzl"]
                os.execle(executable, *args, os.environ)
                sys.exit(0)
        except Exception as e:
            print(str(e))


async def install_externalrepo(repo, branch, cfolder):
    # ... (نفس الكود الأصلي)
    zedREPO = repo
    rpath = os.path.join(cfolder, "requirements.txt")
    if zedBRANCH := branch:
        repourl = os.path.join(zedREPO, f"tree/{zedBRANCH}")
        gcmd = f"git clone -b {zedBRANCH} {zedREPO} {cfolder}"
        errtext = f"There is no branch with name `{zedBRANCH}`"
    else:
        repourl = zedREPO
        gcmd = f"git clone {zedREPO} {cfolder}"
        errtext = f"The link({zedREPO}) is invalid"
    response = urllib.request.urlopen(repourl)
    if response.code != 200:
        LOGS.error(errtext)
        return await zedub.tgbot.send_message(BOTLOG_CHATID, errtext)
    await runcmd(gcmd)
    if not os.path.exists(cfolder):
        LOGS.error("- حدث خطأ اثناء استدعاء رابط الملفات الاضافية")
        return await zedub.tgbot.send_message(BOTLOG_CHATID, "**- حدث خطأ**",)
    if os.path.exists(rpath):
        await runcmd(f"pip3 install --no-cache-dir -r {rpath}")
    await load_plugins(folder="zlzl", extfolder=cfolder)