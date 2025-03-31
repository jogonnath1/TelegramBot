import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext

# 🔹 তোমার টেলিগ্রাম বটের API টোকেন এখানে বসাও
TOKEN = "7958714981:AAGtL6gMzrvevBK2S8osBAcPVW-GqdWTNxs"

# 🔹 গ্রুপের ID (এখানে টপিক ID ব্যবহার করো না, শুধু গ্রুপ ID)
GROUP_ID = -1002483552499

# 🔹 নির্দিষ্ট সাব-টপিক (Thread) ID লিস্ট
TOPIC_IDS = {
    501: "💻 Task Annoucement",  # ✅ থ্রেড ৫০১ এর জন্য বাংলা শিরোনাম
    694: "📢 Important Annoucement",  # ✅ থ্রেড ৬৯৪ এর জন্য বাংলা শিরোনাম
}

# 🔹 লগিং সেটআপ (বাগ ফিক্সের জন্য)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 🔹 গ্রুপ মেম্বারদের ID সংরক্ষণ করতে একটি সেট
group_members = set()

async def forward_message(update: Update, context: CallbackContext) -> None:
    """যখন নির্দিষ্ট থ্রেডে মেসেজ পাঠানো হবে, তখন সেটা ব্যক্তিগতভাবে ফরোয়ার্ড হবে নির্দিষ্ট শিরোনাম সহ"""
    message = update.message
    if message and message.is_topic_message:  # ✅ শুধুমাত্র সাব-টপিকের মেসেজ নিবে
        topic_id = message.message_thread_id
        if topic_id in TOPIC_IDS:
            topic_title = TOPIC_IDS[topic_id]  # ✅ নির্দিষ্ট থ্রেডের বাংলা শিরোনাম
            text = f"**{topic_title} থেকে নতুন বার্তা:**\n\n{message.text}"

            # ✅ শুধুমাত্র ব্যক্তিগত মেসেজ পাঠাবে (গ্রুপে আর মেসেজ পাঠাবে না)
            for user_id in group_members:
                try:
                    await context.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
                except Exception as e:
                    logging.warning(f"❌ {user_id} কে মেসেজ পাঠানো যায়নি: {e}")

async def start(update: Update, context: CallbackContext) -> None:
    """যখন কেউ /start কমান্ড পাঠাবে, তখন তাদের আইডি গ্রুপ মেম্বার লিস্টে যোগ করা হবে"""
    user = update.message.from_user
    group_members.add(user.id)
    await update.message.reply_text("🤖 তুমি এখন সাবস্ক্রাইব করেছো! 📢 সকল Annoucement মেসেজ পাবে।")

def main():
    """বট চালু করার জন্য মেইন ফাংশন"""
    app = Application.builder().token(TOKEN).build()

    # ✅ /start কমান্ড হ্যান্ডলার (প্রতিটি মেম্বারের আইডি সংরক্ষণ করবে)
    app.add_handler(CommandHandler("start", start))

    # ✅ মেসেজ ফরোয়ার্ডার হ্যান্ডলার (শুধুমাত্র সাব-টপিকের মেসেজ নিবে)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    # ✅ বট চালু করা
    app.run_polling()

if __name__ == "__main__":
    main()
