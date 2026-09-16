import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

QUESTIONS = [
    ("What does 'How are you?' mean?", ["كيف حالك؟", "ما اسمك؟", "أين تسكن؟", "كم عمرك؟"], 0),
    ("What does 'Good morning' mean?", ["مساء الخير", "صباح الخير", "تصبح على خير", "أهلاً وسهلاً"], 1),
    ("What does 'Thank you' mean?", ["شكراً", "عفواً", "آسف", "من فضلك"], 0),
    ("What does 'See you tomorrow' mean?", ["أراك اليوم", "أراك غداً", "أراك لاحقاً", "وداعاً"], 1),
    ("What does 'I am hungry' mean?", ["أنا عطشان", "أنا متعب", "أنا جائع", "أنا سعيد"], 2),
    ("What does 'I am tired' mean?", ["أنا متعب", "أنا خائف", "أنا جائع", "أنا مشغول"], 0),
    ("What does 'Where are you going?' mean?", ["متى ستعود؟", "أين أنت؟", "إلى أين أنت ذاهب؟", "من أنت؟"], 2),
    ("What does 'What is your name?' mean?", ["ما اسمك؟", "كم عمرك؟", "أين بيتك؟", "كيف حالك؟"], 0),
    ("What does 'I don't know' mean?", ["أنا أعرف", "لا أعرف", "لا أريد", "لا أستطيع"], 1),
    ("What does 'Please help me' mean?", ["انتظرني", "ساعدني من فضلك", "اتصل بي", "تعال معي"], 1),
    ("What does 'Open the door' mean?", ["افتح الباب", "أغلق الباب", "افتح النافذة", "ادخل الغرفة"], 0),
    ("What does 'Close the window' mean?", ["افتح النافذة", "أغلق الباب", "أغلق النافذة", "نظف النافذة"], 2),
    ("What does 'I love English' mean?", ["أنا أتعلم العربية", "أنا أحب الإنجليزية", "أنا أتكلم بسرعة", "أنا أقرأ كتاباً"], 1),
    ("What does 'Wait a minute' mean?", ["انتظر دقيقة", "تعال بسرعة", "اذهب الآن", "اجلس هنا"], 0),
    ("What does 'Come with me' mean?", ["انتظرني", "تعال معي", "اتصل بي", "اذهب معي غداً"], 1),
    ("What does 'How much is this?' mean?", ["ما هذا؟", "كم سعر هذا؟", "أين هذا؟", "لمن هذا؟"], 1),
    ("What does 'I need water' mean?", ["أحتاج ماءً", "أريد طعاماً", "أحب الماء", "أشرب الماء"], 0),
    ("What does 'I am ready' mean?", ["أنا مشغول", "أنا جاهز", "أنا متأخر", "أنا مريض"], 1),
    ("What does 'Don't worry' mean?", ["لا تتأخر", "لا تنسَ", "لا تقلق", "لا تتكلم"], 2),
    ("What does 'Be careful' mean?", ["كن حذراً", "كن سعيداً", "كن سريعاً", "كن هادئاً"], 0),
    ("What does 'I understand' mean?", ["أنا أفهم", "أنا أوافق", "أنا أتذكر", "أنا أتعلم"], 0),
    ("What does 'Can you repeat?' mean?", ["هل تستطيع الانتظار؟", "هل يمكنك التكرار؟", "هل يمكنك المساعدة؟", "هل تستطيع القراءة؟"], 1),
    ("What does 'Speak slowly' mean?", ["تكلم بصوت عالٍ", "تكلم ببطء", "تكلم بالإنجليزية", "لا تتكلم"], 1),
    ("What does 'Have a nice day' mean?", ["ليلة سعيدة", "أتمنى لك يوماً سعيداً", "صباح الخير", "إلى اللقاء"], 1),
    ("What does 'See you later' mean?", ["أراك لاحقاً", "أراك غداً", "أنا متأخر", "تعال لاحقاً"], 0),
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("📝 ابدأ اختبار اليوم", callback_data="start_quiz")
    ]]

    await update.message.reply_text(
        "📚 برنامج الـ5000 جملة الإنجليزية\n\n"
        "مرحباً بك في الاختبار التجريبي 👋\n\n"
        "📝 عدد الأسئلة: 25\n"
        "🎯 اختر الترجمة الصحيحة لكل جملة.\n\n"
        "اضغط الزر للبدء 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def send_question(query, context):
    index = context.user_data["index"]

    if index >= len(QUESTIONS):
        await finish_quiz(query, context)
        return

    question, options, correct = QUESTIONS[index]

    choices = list(enumerate(options))
    random.shuffle(choices)

    keyboard = [
        [InlineKeyboardButton(text, callback_data=f"answer:{original_index}")]
        for original_index, text in choices
    ]

    await query.edit_message_text(
        f"📖 السؤال {index + 1} من 25\n\n"
        f"🇬🇧 {question}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def finish_quiz(query, context):
    score = context.user_data["score"]
    total = len(QUESTIONS)
    wrong = total - score
    percentage = round((score / total) * 100)

    keyboard = [[
        InlineKeyboardButton("🔄 إعادة الاختبار", callback_data="start_quiz")
    ]]

    await query.edit_message_text(
        "🏁 انتهى الاختبار!\n\n"
        f"✅ الإجابات الصحيحة: {score}/{total}\n"
        f"❌ الإجابات الخاطئة: {wrong}/{total}\n"
        f"📊 النتيجة: {percentage}%\n\n"
        "📚 برنامج الـ5000 جملة الإنجليزية",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_quiz":
        context.user_data["index"] = 0
        context.user_data["score"] = 0
        await send_question(query, context)
        return

    if query.data.startswith("answer:"):
        index = context.user_data.get("index", 0)

        if index >= len(QUESTIONS):
            return

        selected = int(query.data.split(":")[1])
        correct = QUESTIONS[index][2]

        if selected == correct:
            context.user_data["score"] += 1

        context.user_data["index"] += 1
        await send_question(query, context)


def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))

    print("5000 English Quiz Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
