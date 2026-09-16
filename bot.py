import os
import random
import psycopg2

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================================================
# 75 جملة - 3 مستويات - 25 جملة لكل مستوى
# =========================================================

SENTENCES = [
    # المستوى الأول 1-25
    ("The power went out.", "طفت الكهرباء."),
    ("I'm dying to know.", "اموت واعرف."),
    ("You distract me.", "انت دتلهيني."),
    ("Who cares?", "منو مهتم / طز."),
    ("Don't play dumb.", "لا تغشم نفسك."),
    ("Break a leg.", "موفق _ بالتوفيق."),
    ("Wait your turn.", "انتظر سراك."),
    ("Crocodile tears.", "دموع التماسيح."),
    ("I'm exhausted.", "ميت من التعب _ منتهي."),
    ("Eat your heart out.", "موت قهر، موت بدمك."),
    ("Have fun.", "استمتع (تونس)."),
    ("Behave yourself.", "تأدب _ صير آدمي."),
    ("I feel blue.", "اني كلش ضايج."),
    ("The choice is yours.", "القرار قرارك."),
    ("Add fuel to the fire.", "يزيد الطين بله / اجه يكحلها عماها."),
    ("Hug me.", "عانقني _ أشبكني."),
    ("Are you still awake?", "بعدك كاعد ما نايم؟"),
    ("Easy does it.", "على كيفك على راحتك _ لا تستعجل."),
    ("Against my will.", "غصبا عليه."),
    ("You're fired.", "انت مطرود _ توكل ع الله."),
    ("You betrayed me.", "انت خنتني، ضحكت عليه."),
    ("I'm starving.", "ميت من الجوع."),
    ("Don't embarrass me.", "لا تحرجني، غيّر الموضوع."),
    ("I'm sick of you.", "طكت روحي منك _ مليت منك."),
    ("Don't get me wrong.", "لا تفهمني غلط."),

    # المستوى الثاني 26-50
    ("I overslept.", "اخذتني النومه."),
    ("All in all.", "على العموم . على كلاً."),
    ("I'm about to cry.", "راح ابجي."),
    ("It's up to me.", "بكيفي . بمزاجي."),
    ("I dare you.", "اتحداك _ فنك تسويها."),
    ("I'm so depressed.", "طالعه روحي."),
    ("Don't be stingy.", "لا تصير بخيل _ لا تصير ابو فليس."),
    ("Control yourself.", "سيطر على روحك _ استهدي بالله _ اكعد راحه."),
    ("You are overreacting.", "انتِ تبالغين _ تكبرين السالفه . تسوي من الحبه كبه."),
    ("Are you deaf?", "شبيك انت اطرش؟"),
    ("Depression.", "ضوجه فول."),
    ("He abandoned me.", "عافني _ تركني."),
    ("I'm pregnant.", "اني حامل (كيان بالطريق)."),
    ("My pleasure.", "صدك جذب تدلل بعد كلبي _ جسر للطيبين _ بخدمتك."),
    ("Over my dead body.", "على جثتي _ الا اندفن بالتراب _ الا اصير جوه الكاع."),
    ("You rock.", "انت دره . انت ورده مال الله."),
    ("It serves you right.", "طبك مرض حيل بيك زايد . تستاهل الي صار وياك."),
    ("Mark my words.", "تذكر كلامي . خليها ترجيه بأذنك."),
    ("Say that one more time.", "اذا انت زلمه عيدها."),
    ("Let's talk turkey.", "خل نحجي طك بطك."),
    ("Watch out.", "ديربالك يمعود انتبه."),
    ("I have had it.", "طفح الكيل . ترى وصلت حدها."),
    ("I'm out.", "خل انسحب . شورطني خل افلت احسن . اركض اخوي عامر."),
    ("Keep in touch.", "لا تكطع بينا خلينا ع تواصل."),
    ("All kidding aside.", "عوف الشقه على صفحه."),

    # المستوى الثالث 51-75
    ("We broke up.", "انفصلنا كل واحد راح بدربه."),
    ("I'm broke.", "مفلس ، على الحديده ربع مابجيبي."),
    ("You're hopeless.", "غاسل ايدي منك ، كل فايده مامنك."),
    ("Don't threaten me.", "لا تهددني لا تصير سبع براسي."),
    ("Point taken.", "وصلت الفكره _ فهمت قصدك."),
    ("It was a special day.", "يابه جان يوم كلش مميز."),
    ("No offense.", "ما اقصد اهينك _ مو قصدي والله."),
    ("From now on.", "منا ورايح / منا وجاي."),
    ("Just in case.", "بس للأحتياط."),
    ("Don't despair.", "لا تأيس."),
    ("Don't be a pushover.", "لا تصير ضعيف الشخصية."),
    ("I passed out.", "فقدت الوعي _ انغمى عليه."),
    ("One of a kind.", "ماله مثيل _ ماكو منه."),
    ("You're in my thoughts.", "انت على بالي."),
    ("Pray for me.", "ادعيلي."),
    ("I can't stand you.", "ما اطيقك _ ولا تنبلع."),
    ("I dyed my hair.", "صبغت شعري."),
    ("Cheer up.", "افرح هي الدنيا خلصانه."),
    ("I feel guilty.", "حسيت بذنبي _ حسيت بغلطي."),
    ("Pull over.", "اركن السيارة _ اطبك على صفحه."),
    ("Rest in peace.", "الله يرحمه."),
    ("I'm furious.", "روحي واصله لخشمي _ ترى روحي طافره _ معطب."),
    ("Dig in.", "مد ايدك للأكل _ تفضل."),
    ("Here you go.", "هاك اخذ."),
    ("God knows.", "الله أعلم _ بس الله يدري."),
]

LEVELS = {
    1: SENTENCES[0:25],
    2: SENTENCES[25:50],
    3: SENTENCES[50:75],
}

PASS_SCORE = 16


# =========================================================
# قاعدة البيانات
# =========================================================

def get_connection():
    return psycopg2.connect(DATABASE_URL)


def setup_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            unlocked_level INTEGER DEFAULT 1,
            level1_score INTEGER DEFAULT 0,
            level2_score INTEGER DEFAULT 0,
            level3_score INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def register_student(user):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students
        (telegram_id, username, first_name, unlocked_level)
        VALUES (%s, %s, %s, 1)
        ON CONFLICT (telegram_id)
        DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name
    """, (
        user.id,
        user.username,
        user.first_name,
    ))

    conn.commit()
    cur.close()
    conn.close()


def get_student(telegram_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT unlocked_level,
               level1_score,
               level2_score,
               level3_score
        FROM students
        WHERE telegram_id = %s
    """, (telegram_id,))

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result


def save_result(telegram_id, level, score):
    conn = get_connection()
    cur = conn.cursor()

    score_column = f"level{level}_score"

    cur.execute(
        f"""
        UPDATE students
        SET {score_column} =
            GREATEST({score_column}, %s)
        WHERE telegram_id = %s
        """,
        (score, telegram_id)
    )

    # النجاح يفتح المستوى التالي
    if score >= PASS_SCORE and level < 3:
        cur.execute("""
            UPDATE students
            SET unlocked_level =
                GREATEST(unlocked_level, %s)
            WHERE telegram_id = %s
        """, (level + 1, telegram_id))

    conn.commit()
    cur.close()
    conn.close()


# =========================================================
# القائمة الرئيسية
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    register_student(user)

    student = get_student(user.id)

    unlocked = student[0]

    keyboard = []

    keyboard.append([
        InlineKeyboardButton(
            "📝 المستوى الأول",
            callback_data="level:1"
        )
    ])

    if unlocked >= 2:
        keyboard.append([
            InlineKeyboardButton(
                "📝 المستوى الثاني 🔓",
                callback_data="level:2"
            )
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(
                "🔒 المستوى الثاني",
                callback_data="locked:2"
            )
        ])

    if unlocked >= 3:
        keyboard.append([
            InlineKeyboardButton(
                "📝 المستوى الثالث 🔓",
                callback_data="level:3"
            )
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(
                "🔒 المستوى الثالث",
                callback_data="locked:3"
            )
        ])

    text = (
        "📚 برنامج الـ5000 جملة الإنجليزية\n\n"
        f"👋 أهلاً {user.first_name or ''}\n\n"
        "🎯 لديك 3 اختبارات.\n"
        "📝 كل اختبار يحتوي على 25 سؤالاً.\n\n"
        "🔐 لفتح المستوى التالي يجب أن تحصل على "
        "أكثر من 60%.\n"
        "أي 16 إجابة صحيحة من أصل 25 على الأقل.\n\n"
        "اختر المستوى 👇"
    )

    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# =========================================================
# بدء الاختبار
# =========================================================

async def begin_level(query, context, level):
    user = query.from_user

    register_student(user)

    student = get_student(user.id)
    unlocked = student[0]

    if level > unlocked:
        await query.answer(
            "🔒 يجب أن تنجح في المستوى السابق أولاً.",
            show_alert=True
        )
        return

    context.user_data["level"] = level
    context.user_data["question_index"] = 0
    context.user_data["score"] = 0

    await send_question(query, context)


# =========================================================
# إرسال السؤال
# =========================================================

async def send_question(query, context):
    level = context.user_data["level"]
    index = context.user_data["question_index"]

    questions = LEVELS[level]

    if index >= len(questions):
        await finish_quiz(query, context)
        return

    english, correct_arabic = questions[index]

    # نأخذ 3 ترجمات خاطئة من نفس المستوى
    wrong_answers = [
        arabic
        for _, arabic in questions
        if arabic != correct_arabic
    ]

    wrong_answers = random.sample(wrong_answers, 3)

    options = wrong_answers + [correct_arabic]

    random.shuffle(options)

    keyboard = []

    for option in options:
        if option == correct_arabic:
            data = "answer:1"
        else:
            data = "answer:0"

        keyboard.append([
            InlineKeyboardButton(
                option,
                callback_data=data
            )
        ])

    text = (
        f"📚 المستوى {level}\n"
        f"📝 السؤال {index + 1} من 25\n\n"
        f"🇺🇸 {english}\n\n"
        "اختر الترجمة الصحيحة 👇"
    )

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# استقبال الإجابة
# =========================================================

async def answer_question(query, context, correct):
    if "level" not in context.user_data:
        await query.answer(
            "ابدأ الاختبار من /start",
            show_alert=True
        )
        return

    if correct:
        context.user_data["score"] += 1

    context.user_data["question_index"] += 1

    await send_question(query, context)


# =========================================================
# نهاية الاختبار
# =========================================================

async def finish_quiz(query, context):
    level = context.user_data["level"]
    score = context.user_data["score"]

    total = 25
    wrong = total - score
    percentage = round((score / total) * 100)

    user_id = query.from_user.id

    save_result(user_id, level, score)

    if score >= PASS_SCORE:

        if level < 3:
            text = (
                "🎉 مبروك، نجحت!\n\n"
                f"📚 المستوى: {level}\n"
                f"✅ الصحيحة: {score}/25\n"
                f"❌ الخاطئة: {wrong}/25\n"
                f"📊 النتيجة: {percentage}%\n\n"
                f"🔓 تم فتح المستوى {level + 1} لك."
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        f"🚀 ابدأ المستوى {level + 1}",
                        callback_data=f"level:{level + 1}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🏠 القائمة الرئيسية",
                        callback_data="home"
                    )
                ]
            ]

        else:
            text = (
                "🏆 مبروك!\n\n"
                "لقد أكملت المستويات الثلاثة بنجاح 🎉\n\n"
                f"✅ الصحيحة: {score}/25\n"
                f"❌ الخاطئة: {wrong}/25\n"
                f"📊 النتيجة: {percentage}%\n\n"
                "📚 أكملت أول 75 جملة من برنامج "
                "الـ5000 جملة الإنجليزية."
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🏠 القائمة الرئيسية",
                        callback_data="home"
                    )
                ]
            ]

    else:

        text = (
            "📚 لم تجتز المستوى بعد.\n\n"
            f"📚 المستوى: {level}\n"
            f"✅ الصحيحة: {score}/25\n"
            f"❌ الخاطئة: {wrong}/25\n"
            f"📊 النتيجة: {percentage}%\n\n"
            "🔒 المستوى التالي ما زال مغلقاً.\n\n"
            "تحتاج إلى 16 إجابة صحيحة على الأقل "
            "للانتقال للمستوى التالي.\n\n"
            "راجع الجمل ثم حاول مرة أخرى 💪"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔄 إعادة الاختبار",
                    callback_data=f"level:{level}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 القائمة الرئيسية",
                    callback_data="home"
                )
            ]
        ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data.clear()


# =========================================================
# الأزرار
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    data = query.data

    if data == "home":
        await query.answer()
        await start(update, context)
        return

    if data.startswith("locked:"):
        await query.answer(
            "🔒 يجب أن تنجح في المستوى السابق أولاً.",
            show_alert=True
        )
        return

    if data.startswith("level:"):
        await query.answer()

        level = int(data.split(":")[1])

        await begin_level(
            query,
            context,
            level
        )
        return

    if data.startswith("answer:"):
        await query.answer()

        correct = int(data.split(":")[1])

        await answer_question(
            query,
            context,
            correct
        )
        return


# =========================================================
# تشغيل البوت
# =========================================================

def main():

    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing."
        )

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is missing."
        )

    setup_database()

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    print("5000 English Quiz Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
