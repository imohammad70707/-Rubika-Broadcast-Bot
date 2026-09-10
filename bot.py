import asyncio
import json
import os

from maxrubika import Bot
from maxrubika.bot.message import MessageDecorators


GROUPS_FILE = "/storage/emulated/0/groups.json"

bot = Bot()


def load_groups():
    try:
        with open(GROUPS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_groups():
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)


groups = load_groups()
waiting_for_send = set()


# -------------------------
# COMMAND HELPER
# -------------------------

def command(name):
    return bot.on_command(name)


# -------------------------
# START
# -------------------------

@command("start")
async def start_handler(bot, event):
    chat_id = event.chat_id

    await bot.send_message(
        chat_id=chat_id,
        text=(
            "🤖 ربات ارسال همگانی فعال است.\n\n"
            "/start - شروع ربات\n"
            "/groups - لیست گروه‌ها\n"
            "/send - ارسال پیام به گروه‌ها\n"
            "/cancel - لغو ارسال\n"
            "/help - راهنما"
        )
    )

    if chat_id.startswith("g") and chat_id not in groups:
        groups.append(chat_id)
        save_groups()
        print(f"✅ Group saved: {chat_id}")


# -------------------------
# GROUPS
# -------------------------

@command("groups")
async def groups_handler(bot, event):
    chat_id = event.chat_id

    if not groups:
        text = "📋 هیچ گروهی ثبت نشده است."
    else:
        text = "📋 گروه‌های ثبت‌شده:\n\n"

        for i, group_id in enumerate(groups, 1):
            text += f"{i}. {group_id}\n"

        text += f"\n📦 مجموع: {len(groups)} گروه"

    await bot.send_message(
        chat_id=chat_id,
        text=text
    )


# -------------------------
# HELP
# -------------------------

@command("help")
async def help_handler(bot, event):
    await bot.send_message(
        chat_id=event.chat_id,
        text=(
            "📚 راهنمای ربات\n\n"
            "/start\n"
            "شروع ربات\n\n"
            "/groups\n"
            "نمایش گروه‌های ثبت‌شده\n\n"
            "/send\n"
            "ارسال پیام به تمام گروه‌ها\n\n"
            "/cancel\n"
            "لغو عملیات ارسال"
        )
    )


# -------------------------
# SEND
# -------------------------

@command("send")
async def send_handler(bot, event):
    chat_id = event.chat_id

    waiting_for_send.add(chat_id)

    await bot.send_message(
        chat_id=chat_id,
        text=(
            "📨 پیام موردنظر برای ارسال همگانی را بفرست.\n\n"
            "برای لغو:\n"
            "/cancel"
        )
    )


# -------------------------
# CANCEL
# -------------------------

@command("cancel")
async def cancel_handler(bot, event):
    chat_id = event.chat_id

    if chat_id in waiting_for_send:
        waiting_for_send.discard(chat_id)

        await bot.send_message(
            chat_id=chat_id,
            text="❌ عملیات لغو شد."
        )


# -------------------------
# NORMAL MESSAGE
# -------------------------

@bot.on_new_message()
async def normal_message(bot, event):

    chat_id = event.chat_id
    message = event.message or {}

    text = message.get("text", "")

    print("\n🔎 NEW MESSAGE HANDLER")
    print(f"CHAT: {chat_id}")
    print(f"MESSAGE: {message}")

    if not text:
        return

    if text.startswith("/"):
        return

    if chat_id not in waiting_for_send:
        return

    waiting_for_send.discard(chat_id)

    if not groups:
        await bot.send_message(
            chat_id=chat_id,
            text="❌ هیچ گروهی ثبت نشده است."
        )
        return

    await bot.send_message(
        chat_id=chat_id,
        text=f"🚀 شروع ارسال به {len(groups)} گروه..."
    )

    success = 0
    failed = 0

    for group_id in groups:

        try:
            result = await bot.send_message(
                chat_id=group_id,
                text=text
            )

            print(f"✅ Sent → {group_id}")
            print(result)

            success += 1

        except Exception as e:

            print(f"❌ Failed → {group_id}")
            print(e)

            failed += 1

        await asyncio.sleep(0.5)

    await bot.send_message(
        chat_id=chat_id,
        text=(
            "📊 گزارش ارسال\n\n"
            f"✅ موفق: {success}\n"
            f"❌ ناموفق: {failed}\n"
            f"📦 مجموع: {len(groups)}"
        )
    )


# -------------------------
# RUN
# -------------------------

print("🤖 Bot is connecting...")
bot.run()
