import logging
from telegram import Update, ChatMember
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext

# 🔹 তোমার টেলিগ্রাম বটের API টোকেন এখানে বসাও
TOKEN = "7958714981:AAGtL6gMzrvevBK2S8osBAcPVW-GqdWTNxs"

# 🔹 গ্রুপের ID
GROUP_ID = -1002483552499

# 🔹 নির্দিষ্ট সাব-টপিক (Thread) ID লিস্ট
TOPIC_IDS = {
    501: "💻 Task Announcement",
    694: "📢 Important Announcement",
}

# 🔹 লগিং সেটআপ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 🔹 গ্রুপ মেম্বারদের ID সংরক্ষণ করতে একটি সেট
group_members = set()

async def fetch_group_members(context: CallbackContext) -> None:
    """বট রিস্টার্ট হলে গ্রুপের সদস্যদের আইডি সংগ্রহ করা"""
    try:
        chat_admins = await context.bot.get_chat_administrators(GROUP_ID)
        for admin in chat_admins:
            group_members.add(admin.user.id)
        logging.info(f"✅ গ্রুপ মেম্বার লোড হয়েছে: {len(group_members)} জন")
    except Exception as e:
        logging.warning(f"❌ গ্রুপ মেম্বার লোড করতে সমস্যা: {e}")

async def forward_message(update: Update, context: CallbackContext) -> None:
    """নির্দিষ্ট থ্রেডের মেসেজ ফরোয়ার্ড করবে"""
    message = update.message
    if message and message.is_topic_message:
        topic_id = message.message_thread_id
        if topic_id in TOPIC_IDS:
            topic_title = TOPIC_IDS[topic_id]
            text = f"**{topic_title} থেকে নতুন বার্তা:**\n\n{message.text}"

            failed_users = []  # যাদের মেসেজ পাঠানো যায়নি, তাদের লিস্ট

            for user_id in group_members:
                try:
                    await context.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
                except Exception as e:
                    logging.warning(f"❌ {user_id} কে মেসেজ পাঠানো যায়নি: {e}")
                    failed_users.append(f"[User](tg://user?id={user_id})")  # Mention লিস্টে যোগ

            # যদি কেউ মেসেজ না পায়, তাদের `/start` দিতে বলা হবে
            if failed_users:
                mention_list = ", ".join(failed_users)
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=f"⚠️ নিচের ইউজাররা এখনও `/start` করেননি, তাই তারা গুরুত্বপূর্ণ নোটিফিকেশন পাচ্ছেন না! অনুগ্রহ করে `/start` দিন:\n{mention_list}",
                    parse_mode="Markdown"
                )

async def start(update: Update, context: CallbackContext) -> None:
    """যখন কেউ /start কমান্ড পাঠাবে, তখন তাদের আইডি সংরক্ষণ করবে"""
    user = update.message.from_user
    group_members.add(user.id)
    await update.message.reply_text("✅ তুমি এখন সাবস্ক্রাইব করেছো! 📢 সকল CP Announcements পাবে।")

async def member_update(update: Update, context: CallbackContext) -> None:
    """যখন নতুন সদস্য গ্রুপে যোগ হবে, তখন তাকে সংরক্ষণ করা হবে"""
    chat_member = update.chat_member
    if chat_member.new_chat_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        group_members.add(chat_member.new_chat_member.user.id)

async def init_jobs(app: Application) -> None:
    """বট চালু হলে গ্রুপের মেম্বার লোড করবে"""
    await fetch_group_members(CallbackContext(app))

async def error_handler(update: object, context: CallbackContext) -> None:
    logging.error(f"❌ ত্রুটি হয়েছে: {context.error}")

def main():
    """বট চালু করার জন্য মেইন ফাংশন"""
    app = Application.builder().token(TOKEN).post_init(init_jobs).build()

    # ✅ /start কমান্ড হ্যান্ডলার
    app.add_handler(CommandHandler("start", start))

    # ✅ মেম্বার যোগ হলে সংরক্ষণ করবে
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, member_update))

    # ✅ মেসেজ ফরোয়ার্ডার হ্যান্ডলার
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    # ✅ ত্রুটি হ্যান্ডলার
    app.add_error_handler(error_handler)

    # ✅ বট চালু করা
    app.run_polling()

if __name__ == "__main__":
    main()
