import inspect
import re
import sys
import traceback
from pathlib import Path

from .. import CMD_LIST, LOAD_PLUG, SUDO_LIST
from ..Config import Config
from ..core.data import _sudousers_list, blacklist_chats_list
from ..core.events import MessageEdited, NewMessage
from ..core.logger import logging
from ..core.session import zedub
from ..helpers.utils.format import paste_message
from ..helpers.utils.utils import runcmd
from ..sql_helper.globals import gvarstatus

LOGS = logging.getLogger(__name__)

# دالة لتجهيز النمط (Regex) بشكل آمن
def compile_pattern(pattern, handler):
    if pattern.startswith(r"\#"):
        return re.compile(pattern), pattern
    elif pattern.startswith(r"^"):
        return re.compile(pattern), pattern
    
    # تنظيف الهاندلر (النقطة)
    try:
        if len(handler) == 1:
            zedreg = "^\\" + handler
        else:
            zedreg = "^" + handler
    except:
        zedreg = "^\\." # افتراضي نقطة

    return re.compile(zedreg + pattern), handler + pattern

def admin_cmd(pattern=None, command=None, **args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    allow_sudo = args.get("allow_sudo", False)
    
    # التأكد من الهاندلر
    hand_ler = Config.COMMAND_HAND_LER or "."

    if pattern is not None:
        try:
            compiled_reg, cmd_text = compile_pattern(pattern, hand_ler)
            args["pattern"] = compiled_reg
            
            # تنظيف اسم الأمر للقائمة
            if command is not None:
                cmd = hand_ler + command
            else:
                cmd = cmd_text.replace("$", "").replace("\\", "").replace("^", "")
                
            # إضافة للقائمة بأمان
            if file_test not in CMD_LIST:
                CMD_LIST[file_test] = []
            CMD_LIST[file_test].append(cmd)
        except Exception as e:
            LOGS.error(f"Error registering admin_cmd in {file_test}: {e}")

    args["outgoing"] = True
    if allow_sudo:
        args["from_users"] = list(Config.SUDO_USERS)
        args["incoming"] = True
        del args["allow_sudo"]
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True
        
    if gvarstatus("blacklist_chats") is not None:
        args["blacklist_chats"] = True
        args["chats"] = blacklist_chats_list()
        
    if "allow_edited_updates" in args and args["allow_edited_updates"]:
        del args["allow_edited_updates"]
        
    return NewMessage(**args)


def sudo_cmd(pattern=None, command=None, **args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    allow_sudo = args.get("allow_sudo", False)
    
    # التأكد من الهاندلر
    hand_ler = Config.SUDO_COMMAND_HAND_LER or "."

    if pattern is not None:
        try:
            compiled_reg, cmd_text = compile_pattern(pattern, hand_ler)
            args["pattern"] = compiled_reg
            
            if command is not None:
                cmd = hand_ler + command
            else:
                cmd = cmd_text.replace("$", "").replace("\\", "").replace("^", "")

            if file_test not in SUDO_LIST:
                SUDO_LIST[file_test] = []
            SUDO_LIST[file_test].append(cmd)
        except Exception as e:
            LOGS.error(f"Error registering sudo_cmd in {file_test}: {e}")

    args["outgoing"] = True
    if allow_sudo:
        args["from_users"] = list(_sudousers_list())
        args["incoming"] = True
        del args["allow_sudo"]
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True
        
    if gvarstatus("blacklist_chats") is not None:
        args["blacklist_chats"] = True
        args["chats"] = blacklist_chats_list()
        
    if "allow_edited_updates" in args and args["allow_edited_updates"]:
        del args["allow_edited_updates"]
        
    if gvarstatus("sudoenable") is not None:
        return NewMessage(**args)


def errors_handler(func):
    async def wrapper(errors):
        try:
            await func(errors)
        except BaseException:
            # تصحيح الخطأ القاتل: تعريف المتغير check
            check = errors
            if Config.PRIVATE_GROUP_BOT_API_ID == 0:
                return
            
            date = (datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
            ftext = f"\n**⚠️ تقرير خطأ تلقائي:**\n"
            ftext += f"\n**التاريخ:** `{date}`"
            ftext += f"\n**الدردشة:** `{str(check.chat_id)}`"
            ftext += f"\n**المرسل:** `{str(check.sender_id)}`"
            ftext += f"\n\n**الأمر:**\n`{str(check.text)}`"
            ftext += f"\n\n**الخطأ:**\n`{str(sys.exc_info()[1])}`"
            
            # محاولة إرسال التقرير
            try:
                await check.client.send_message(
                    Config.PRIVATE_GROUP_BOT_API_ID, ftext, link_preview=False
                )
            except:
                pass # إذا فشل الإرسال لا تقتل البوت

    return wrapper


def register(**args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    pattern = args.get("pattern", None)
    disable_edited = args.get("disable_edited", True)
    allow_sudo = args.get("allow_sudo", False)

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    if "disable_edited" in args:
        del args["disable_edited"]

    # تسجيل الأمر في القوائم
    reg = re.compile("(.*)")
    if pattern is not None:
        try:
            cmd = re.search(reg, pattern)
            try:
                cmd = cmd.group(1).replace("$", "").replace("\\", "").replace("^", "")
            except:
                pass

            if file_test not in CMD_LIST:
                CMD_LIST[file_test] = []
            CMD_LIST[file_test].append(cmd)
        except:
            pass

    if allow_sudo:
        args["from_users"] = list(Config.SUDO_USERS)
        args["incoming"] = True
        del args["allow_sudo"]
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True

    if gvarstatus("blacklist_chats") is not None:
        args["blacklist_chats"] = True
        args["chats"] = blacklist_chats_list()

    def decorator(func):
        if not disable_edited:
            zedub.add_event_handler(func, MessageEdited(**args))
        zedub.add_event_handler(func, NewMessage(**args))
        
        if file_test not in LOAD_PLUG:
            LOAD_PLUG[file_test] = []
        LOAD_PLUG[file_test].append(func)
        return func

    return decorator


def command(**args):
    # دمج command مع register لتوحيد العمل
    return register(**args)