import os
import random
import psycopg2

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_ID = 5428742205

QUESTIONS_PER_LEVEL = 25
PASS_SCORE = 16


# =========================================================
# الجمل الأصلية للمستويات الثلاثة الأولى
# =========================================================

INITIAL_LEVELS = {
    1: [
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
    ],

    2: [
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
    ],

    3: [
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
    ],
}


# =========================================================
# قاعدة البيانات
# =========================================================

def get_connection():
    return psycopg2.connect(DATABASE_URL)


def setup_database():
    conn = get_connection()
    cur = conn.cursor()

    # جدول الطلاب القديم نحافظ عليه
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

    # جدول المستويات
    cur.execute("""
        CREATE TABLE IF NOT EXISTS levels (
            level_number INTEGER PRIMARY KEY,
            title TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)

    # جدول الأسئلة
    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            level_number INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            english TEXT NOT NULL,
            arabic TEXT NOT NULL,
            UNIQUE(level_number, question_number)
        )
    """)

    # جدول نتائج الطلاب الجديد
    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_results (
            telegram_id BIGINT NOT NULL,
            level_number INTEGER NOT NULL,
            best_score INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            passed BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (telegram_id, level_number)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

    seed_initial_levels()
    migrate_old_results()


def seed_initial_levels():
    conn = get_connection()
    cur = conn.cursor()

    for level_number, questions in INITIAL_LEVELS.items():

        cur.execute("""
            INSERT INTO levels (
                level_number,
                title,
                is_active
            )
            VALUES (%s, %s, TRUE)
            ON CONFLICT (level_number)
            DO NOTHING
        """, (
            level_number,
            f"المستوى {level_number}"
        ))

        for number, (english, arabic) in enumerate(
            questions,
            start=1
        ):
            cur.execute("""
                INSERT INTO questions (
                    level_number,
                    question_number,
                    english,
                    arabic
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (
                    level_number,
                    question_number
                )
                DO NOTHING
            """, (
                level_number,
                number,
                english,
                arabic
            ))

    conn.commit()
    cur.close()
    conn.close()


def migrate_old_results():
    """
    ينقل أفضل نتائج المستويات القديمة 1 و2 و3
    إلى جدول النتائج الجديد بدون حذف البيانات القديمة.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            telegram_id,
            level1_score,
            level2_score,
            level3_score
        FROM students
    """)

    rows = cur.fetchall()

    for row in rows:
        telegram_id = row[0]

        scores = {
            1: row[1] or 0,
            2: row[2] or 0,
            3: row[3] or 0,
        }

        for level, score in scores.items():

            if score <= 0:
                continue

            passed = score >= PASS_SCORE

            cur.execute("""
                INSERT INTO student_results (
                    telegram_id,
                    level_number,
                    best_score,
                    attempts,
                    passed
                )
                VALUES (%s, %s, %s, 1, %s)

                ON CONFLICT (
                    telegram_id,
                    level_number
                )
                DO UPDATE SET
                    best_score = GREATEST(
                        student_results.best_score,
                        EXCLUDED.best_score
                    ),
                    passed = (
                        student_results.passed
                        OR EXCLUDED.passed
                    )
            """, (
                telegram_id,
                level,
                score,
                passed
            ))

    conn.commit()
    cur.close()
    conn.close()


# =========================================================
# الطلاب
# =========================================================

def register_student(user):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students (
            telegram_id,
            username,
            first_name
        )
        VALUES (%s, %s, %s)

        ON CONFLICT (telegram_id)
        DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name
    """, (
        user.id,
        user.username,
        user.first_name
    ))

    conn.commit()
    cur.close()
    conn.close()


def get_levels():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT level_number, title
        FROM levels
        WHERE is_active = TRUE
        ORDER BY level_number
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def get_level_questions(level_number):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            question_number,
            english,
            arabic
        FROM questions
        WHERE level_number = %s
        ORDER BY question_number
    """, (level_number,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def get_best_score(telegram_id, level_number):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT best_score
        FROM student_results
        WHERE telegram_id = %s
        AND level_number = %s
    """, (
        telegram_id,
        level_number
    ))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return row[0]

    return 0


def has_passed(telegram_id, level_number):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT passed
        FROM student_results
        WHERE telegram_id = %s
        AND level_number = %s
    """, (
        telegram_id,
        level_number
    ))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return False

    return bool(row[0])


def can_access_level(telegram_id, level_number):

    # المدير إذا فتح وضع الاختبار
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT unlocked_level
        FROM students
        WHERE telegram_id = %s
    """, (telegram_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if (
        telegram_id == ADMIN_ID
        and row
        and row[0] >= level_number
    ):
        return True

    if level_number == 1:
        return True

    return has_passed(
        telegram_id,
        level_number - 1
    )


def save_result(
    telegram_id,
    level_number,
    score
):
    passed = score >= PASS_SCORE

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO student_results (
            telegram_id,
            level_number,
            best_score,
            attempts,
            passed
        )
        VALUES (%s, %s, %s, 1, %s)

        ON CONFLICT (
            telegram_id,
            level_number
        )
        DO UPDATE SET
            best_score = GREATEST(
                student_results.best_score,
                EXCLUDED.best_score
            ),
            attempts =
                student_results.attempts + 1,
            passed = (
                student_results.passed
                OR EXCLUDED.passed
            )
    """, (
        telegram_id,
        level_number,
        score,
        passed
    ))

    conn.commit()
    cur.close()
    conn.close()


# =========================================================
# القائمة الرئيسية
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await show_main_menu(update)


async def show_main_menu(update: Update):

    user = update.effective_user

    register_student(user)

    levels = get_levels()

    keyboard = []

    for level_number, title in levels:

        accessible = can_access_level(
            user.id,
            level_number
        )

        score = get_best_score(
            user.id,
            level_number
        )

        if accessible:

            if score >= PASS_SCORE:
                label = (
                    f"✅ {title} "
                    f"({score}/25)"
                )
            else:
                label = f"📝 {title}"

            callback = f"level:{level_number}"

        else:
            label = f"🔒 {title}"
            callback = f"locked:{level_number}"

        keyboard.append([
            InlineKeyboardButton(
                label,
                callback_data=callback
            )
        ])

    text = (
        "📚 برنامج الـ5000 جملة الإنجليزية\n\n"
        f"👋 أهلاً {user.first_name or ''}\n\n"
        "🎯 كل مستوى يحتوي على 25 سؤالاً.\n\n"
        "🔐 يجب أن تحصل على أكثر من 60% "
        "لفتح المستوى التالي.\n"
        "✅ الحد الأدنى للنجاح: 16 من 25.\n\n"
        "اختر المستوى 👇"
    )

    markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=markup
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=markup
        )


# =========================================================
# بدء الاختبار
# =========================================================

async def begin_level(
    query,
    context,
    level_number
):

    user = query.from_user

    register_student(user)

    if not can_access_level(
        user.id,
        level_number
    ):
        await query.answer(
            "🔒 يجب النجاح في المستوى السابق أولاً.",
            show_alert=True
        )
        return

    questions = get_level_questions(
        level_number
    )

    if len(questions) != QUESTIONS_PER_LEVEL:
        await query.answer(
            "⚠️ هذا المستوى غير مكتمل.",
            show_alert=True
        )
        return

    context.user_data["quiz"] = {
        "level": level_number,
        "index": 0,
        "score": 0,
        "questions": questions,
    }

    await send_question(
        query,
        context
    )


async def send_question(
    query,
    context
):

    quiz = context.user_data.get(
        "quiz"
    )

    if not quiz:
        await query.edit_message_text(
            "انتهت جلسة الاختبار.\n"
            "أرسل /start للبدء."
        )
        return

    index = quiz["index"]
    questions = quiz["questions"]

    if index >= len(questions):
        await finish_quiz(
            query,
            context
        )
        return

    _, english, correct_arabic = (
        questions[index]
    )

    translations = [
        row[2]
        for row in questions
        if row[2] != correct_arabic
    ]

    wrong_answers = random.sample(
        translations,
        3
    )

    options = [
        (correct_arabic, True)
    ]

    for answer in wrong_answers:
        options.append(
            (answer, False)
        )

    random.shuffle(options)

    keyboard = []

    for answer, correct in options:

        value = 1 if correct else 0

        keyboard.append([
            InlineKeyboardButton(
                answer,
                callback_data=f"answer:{value}"
            )
        ])

    text = (
        f"📚 المستوى {quiz['level']}\n"
        f"📝 السؤال {index + 1} من 25\n\n"
        f"🇺🇸 {english}\n\n"
        "اختر الترجمة الصحيحة 👇"
    )

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


async def answer_question(
    query,
    context,
    correct
):

    quiz = context.user_data.get(
        "quiz"
    )

    if not quiz:
        await query.answer(
            "انتهت جلسة الاختبار.",
            show_alert=True
        )
        return

    if correct:
        quiz["score"] += 1

    quiz["index"] += 1

    await send_question(
        query,
        context
    )


async def finish_quiz(
    query,
    context
):

    quiz = context.user_data[
        "quiz"
    ]

    level = quiz["level"]
    score = quiz["score"]

    wrong = (
        QUESTIONS_PER_LEVEL - score
    )

    percentage = round(
        (
            score
            / QUESTIONS_PER_LEVEL
        ) * 100
    )

    save_result(
        query.from_user.id,
        level,
        score
    )

    passed = (
        score >= PASS_SCORE
    )

    levels = [
        row[0]
        for row in get_levels()
    ]

    next_level = None

    if level in levels:
        position = levels.index(level)

        if position + 1 < len(levels):
            next_level = levels[
                position + 1
            ]

    if passed:

        text = (
            "🎉 مبروك، نجحت!\n\n"
            f"📚 المستوى: {level}\n"
            f"✅ الصحيحة: {score}/25\n"
            f"❌ الخاطئة: {wrong}/25\n"
            f"📊 النتيجة: {percentage}%\n"
        )

        keyboard = []

        if next_level is not None:

            text += (
                f"\n🔓 تم فتح المستوى "
                f"{next_level}."
            )

            keyboard.append([
                InlineKeyboardButton(
                    f"🚀 ابدأ المستوى {next_level}",
                    callback_data=(
                        f"level:{next_level}"
                    )
                )
            ])

        else:
            text += (
                "\n🏆 أكملت جميع المستويات "
                "المتوفرة حالياً."
            )

        keyboard.append([
            InlineKeyboardButton(
                "🏠 القائمة الرئيسية",
                callback_data="home"
            )
        ])

    else:

        text = (
            "📚 لم تجتز المستوى بعد.\n\n"
            f"📚 المستوى: {level}\n"
            f"✅ الصحيحة: {score}/25\n"
            f"❌ الخاطئة: {wrong}/25\n"
            f"📊 النتيجة: {percentage}%\n\n"
            "🔒 تحتاج إلى 16 إجابة "
            "صحيحة على الأقل.\n\n"
            "حاول مرة أخرى 💪"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔄 إعادة الاختبار",
                    callback_data=(
                        f"level:{level}"
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 القائمة الرئيسية",
                    callback_data="home"
                )
            ]
        ]

    context.user_data.pop(
        "quiz",
        None
    )

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# =========================================================
# لوحة الإدارة
# =========================================================

def is_admin(user_id):
    return user_id == ADMIN_ID


def admin_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ إضافة مستوى جديد",
                callback_data="admin:add_level"
            )
        ],
        [
            InlineKeyboardButton(
                "📚 إدارة المستويات",
                callback_data="admin:levels"
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ تعديل سؤال",
                callback_data="admin:edit_question"
            )
        ],
        [
            InlineKeyboardButton(
                "🗑️ حذف مستوى",
                callback_data="admin:delete_level"
            )
        ],
        [
            InlineKeyboardButton(
                "👥 عدد الطلاب",
                callback_data="admin:students"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 نتائج الطلاب",
                callback_data="admin:results"
            )
        ],
        [
            InlineKeyboardButton(
                "🧪 فتح المستويات لحسابي",
                callback_data="admin:unlock"
            )
        ],
        [
            InlineKeyboardButton(
                "🔒 إعادة حسابي",
                callback_data="admin:reset"
            )
        ],
    ])


def admin_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM students"
    )
    students = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM levels"
    )
    levels = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM questions"
    )
    questions = cur.fetchone()[0]

    cur.close()
    conn.close()

    return (
        students,
        levels,
        questions
    )


async def admin_panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not is_admin(user.id):
        await update.message.reply_text(
            "⛔ غير مصرح لك بالدخول."
        )
        return

    register_student(user)

    students, levels, questions = (
        admin_stats()
    )

    text = (
        "🔐 لوحة إدارة برنامج الـ5000 جملة\n\n"
        f"👥 الطلاب: {students}\n"
        f"📚 المستويات: {levels}\n"
        f"📝 الأسئلة: {questions}\n\n"
        "اختر العملية التي تريدها 👇"
    )

    await update.message.reply_text(
        text,
        reply_markup=admin_keyboard()
    )


# =========================================================
# إضافة مستوى جديد
# =========================================================

async def start_add_level(
    query,
    context
):

    context.user_data[
        "admin_action"
    ] = "add_level"

    await query.edit_message_text(
        "➕ إضافة مستوى جديد\n\n"
        "أرسل الآن 25 جملة دفعة واحدة.\n\n"
        "كل جملة في سطر مستقل بهذا الشكل:\n\n"
        "English | الترجمة العراقية\n\n"
        "مثال:\n"
        "The power went out. | طفت الكهرباء.\n\n"
        "⚠️ يجب أن يكون العدد 25 سطراً بالضبط.\n\n"
        "لإلغاء العملية أرسل /cancel"
    )


def parse_questions(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    questions = []

    for line in lines:

        if "|" not in line:
            return None

        english, arabic = line.split(
            "|",
            1
        )

        english = english.strip()
        arabic = arabic.strip()

        if not english or not arabic:
            return None

        questions.append(
            (english, arabic)
        )

    return questions


def create_new_level(
    questions
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(
            MAX(level_number),
            0
        )
        FROM levels
    """)

    new_level = (
        cur.fetchone()[0] + 1
    )

    cur.execute("""
        INSERT INTO levels (
            level_number,
            title,
            is_active
        )
        VALUES (%s, %s, TRUE)
    """, (
        new_level,
        f"المستوى {new_level}"
    ))

    for number, (
        english,
        arabic
    ) in enumerate(
        questions,
        start=1
    ):

        cur.execute("""
            INSERT INTO questions (
                level_number,
                question_number,
                english,
                arabic
            )
            VALUES (%s, %s, %s, %s)
        """, (
            new_level,
            number,
            english,
            arabic
        ))

    conn.commit()
    cur.close()
    conn.close()

    return new_level


# =========================================================
# إدارة المستويات
# =========================================================

async def show_admin_levels(
    query
):

    levels = get_levels()

    if not levels:
        text = (
            "📚 لا توجد مستويات."
        )

    else:
        lines = [
            "📚 المستويات الحالية:\n"
        ]

        conn = get_connection()
        cur = conn.cursor()

        for level_number, title in levels:

            cur.execute("""
                SELECT COUNT(*)
                FROM questions
                WHERE level_number = %s
            """, (
                level_number,
            ))

            count = cur.fetchone()[0]

            lines.append(
                f"• {title}: "
                f"{count} سؤال"
            )

        cur.close()
        conn.close()

        text = "\n".join(lines)

    keyboard = [
        [
            InlineKeyboardButton(
                "🔙 لوحة الإدارة",
                callback_data="admin:menu"
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# =========================================================
# تعديل سؤال
# =========================================================

async def start_edit_question(
    query,
    context
):

    context.user_data[
        "admin_action"
    ] = "edit_question"

    await query.edit_message_text(
        "✏️ تعديل سؤال\n\n"
        "أرسل البيانات بهذا الشكل:\n\n"
        "رقم المستوى | رقم السؤال | English | الترجمة\n\n"
        "مثال:\n"
        "2 | 5 | I dare you. | اتحداك\n\n"
        "لإلغاء العملية أرسل /cancel"
    )


def edit_question_from_text(
    text
):

    parts = [
        part.strip()
        for part in text.split("|")
    ]

    if len(parts) != 4:
        return False, (
            "الصيغة غير صحيحة."
        )

    try:
        level = int(parts[0])
        question_number = int(
            parts[1]
        )
    except ValueError:
        return False, (
            "رقم المستوى أو السؤال غير صحيح."
        )

    english = parts[2]
    arabic = parts[3]

    if not english or not arabic:
        return False, (
            "الجملة أو الترجمة فارغة."
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE questions
        SET
            english = %s,
            arabic = %s
        WHERE level_number = %s
        AND question_number = %s
    """, (
        english,
        arabic,
        level,
        question_number
    ))

    changed = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()

    if changed == 0:
        return False, (
            "لم أجد هذا السؤال."
        )

    return True, (
        f"✅ تم تعديل السؤال "
        f"{question_number} "
        f"من المستوى {level}."
    )


# =========================================================
# حذف مستوى
# =========================================================

async def start_delete_level(
    query,
    context
):

    context.user_data[
        "admin_action"
    ] = "delete_level"

    await query.edit_message_text(
        "🗑️ حذف مستوى\n\n"
        "أرسل رقم المستوى الذي تريد حذفه.\n\n"
        "مثال:\n"
        "4\n\n"
        "⚠️ لا يمكن حذف المستويات "
        "1 و2 و3 الأصلية.\n\n"
        "لإلغاء العملية أرسل /cancel"
    )


def delete_level(
    level_number
):

    if level_number <= 3:
        return False, (
            "⛔ لا يمكن حذف "
            "المستويات الأصلية 1 و2 و3."
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 1
        FROM levels
        WHERE level_number = %s
    """, (
        level_number,
    ))

    exists = cur.fetchone()

    if not exists:
        cur.close()
        conn.close()

        return False, (
            "لم أجد هذا المستوى."
        )

    cur.execute("""
        DELETE FROM questions
        WHERE level_number = %s
    """, (
        level_number,
    ))

    cur.execute("""
        DELETE FROM student_results
        WHERE level_number = %s
    """, (
        level_number,
    ))

    cur.execute("""
        DELETE FROM levels
        WHERE level_number = %s
    """, (
        level_number,
    ))

    conn.commit()
    cur.close()
    conn.close()

    return True, (
        f"✅ تم حذف المستوى "
        f"{level_number}."
    )


# =========================================================
# رسائل المدير
# =========================================================

async def admin_text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not is_admin(user.id):
        return

    action = context.user_data.get(
        "admin_action"
    )

    if not action:
        return

    text = update.message.text.strip()

    # إضافة مستوى
    if action == "add_level":

        questions = parse_questions(
            text
        )

        if questions is None:
            await update.message.reply_text(
                "❌ توجد مشكلة في التنسيق.\n\n"
                "استخدم:\n"
                "English | الترجمة\n\n"
                "كل سؤال في سطر مستقل."
            )
            return

        if (
            len(questions)
            != QUESTIONS_PER_LEVEL
        ):
            await update.message.reply_text(
                "❌ العدد غير صحيح.\n\n"
                f"أرسلت: {len(questions)} سؤال\n"
                "المطلوب: 25 سؤال بالضبط.\n\n"
                "أعد إرسال القائمة كاملة."
            )
            return

        new_level = create_new_level(
            questions
        )

        context.user_data.pop(
            "admin_action",
            None
        )

        await update.message.reply_text(
            "✅ تمت إضافة المستوى بنجاح!\n\n"
            f"📚 المستوى: {new_level}\n"
            "📝 عدد الأسئلة: 25\n"
            "🔒 سيفتح للطالب بعد نجاحه "
            "في المستوى السابق.\n\n"
            "أرسل /admin للعودة "
            "إلى لوحة الإدارة."
        )

        return

    # تعديل سؤال
    if action == "edit_question":

        success, message = (
            edit_question_from_text(
                text
            )
        )

        if success:
            context.user_data.pop(
                "admin_action",
                None
            )

        await update.message.reply_text(
            message
        )

        return

    # حذف مستوى
    if action == "delete_level":

        try:
            level_number = int(
                text
            )
        except ValueError:
            await update.message.reply_text(
                "❌ أرسل رقم المستوى فقط."
            )
            return

        success, message = (
            delete_level(
                level_number
            )
        )

        if success:
            context.user_data.pop(
                "admin_action",
                None
            )

        await update.message.reply_text(
            message
        )

        return


# =========================================================
# إلغاء عملية الإدارة
# =========================================================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(
        update.effective_user.id
    ):
        return

    context.user_data.pop(
        "admin_action",
        None
    )

    await update.message.reply_text(
        "✅ تم إلغاء العملية.\n\n"
        "أرسل /admin للعودة "
        "إلى لوحة الإدارة."
    )


# =========================================================
# أزرار الإدارة
# =========================================================

async def admin_button(
    query,
    context,
    data
):

    if not is_admin(
        query.from_user.id
    ):
        await query.answer(
            "⛔ غير مصرح لك.",
            show_alert=True
        )
        return

    # القائمة
    if data == "admin:menu":

        students, levels, questions = (
            admin_stats()
        )

        text = (
            "🔐 لوحة إدارة برنامج الـ5000 جملة\n\n"
            f"👥 الطلاب: {students}\n"
            f"📚 المستويات: {levels}\n"
            f"📝 الأسئلة: {questions}\n\n"
            "اختر العملية 👇"
        )

        await query.edit_message_text(
            text,
            reply_markup=admin_keyboard()
        )
        return

    # إضافة مستوى
    if data == "admin:add_level":
        await start_add_level(
            query,
            context
        )
        return

    # المستويات
    if data == "admin:levels":
        await show_admin_levels(
            query
        )
        return

    # تعديل سؤال
    if data == "admin:edit_question":
        await start_edit_question(
            query,
            context
        )
        return

    # حذف مستوى
    if data == "admin:delete_level":
        await start_delete_level(
            query,
            context
        )
        return

    # عدد الطلاب
    if data == "admin:students":

        students, _, _ = (
            admin_stats()
        )

        await query.answer(
            f"👥 عدد الطلاب: {students}",
            show_alert=True
        )
        return

    # النتائج
    if data == "admin:results":

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                s.telegram_id,
                s.first_name,
                COUNT(r.level_number),
                COALESCE(
                    SUM(
                        CASE
                            WHEN r.passed
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                )
            FROM students s
            LEFT JOIN student_results r
                ON s.telegram_id =
                   r.telegram_id
            GROUP BY
                s.telegram_id,
                s.first_name
            ORDER BY s.telegram_id DESC
            LIMIT 30
        """)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        lines = [
            "📊 نتائج الطلاب\n"
        ]

        if not rows:
            lines.append(
                "لا توجد نتائج حتى الآن."
            )

        for (
            telegram_id,
            name,
            attempted,
            passed
        ) in rows:

            lines.append(
                f"\n👤 {name or 'بدون اسم'}\n"
                f"🆔 {telegram_id}\n"
                f"📝 مستويات مجرّبة: {attempted}\n"
                f"✅ مستويات ناجحة: {passed}"
            )

        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 لوحة الإدارة",
                        callback_data="admin:menu"
                    )
                ]
            ])
        )

        return

    # فتح جميع المستويات للمدير
    if data == "admin:unlock":

        levels = get_levels()

        if levels:
            max_level = max(
                row[0]
                for row in levels
            )
        else:
            max_level = 1

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE students
            SET unlocked_level = %s
            WHERE telegram_id = %s
        """, (
            max_level,
            ADMIN_ID
        ))

        conn.commit()
        cur.close()
        conn.close()

        await query.answer(
            "✅ تم فتح جميع المستويات لحسابك.",
            show_alert=True
        )
        return

    # إعادة حساب المدير
    if data == "admin:reset":

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM student_results
            WHERE telegram_id = %s
        """, (
            ADMIN_ID,
        ))

        cur.execute("""
            UPDATE students
            SET
                unlocked_level = 1,
                level1_score = 0,
                level2_score = 0,
                level3_score = 0
            WHERE telegram_id = %s
        """, (
            ADMIN_ID,
        ))

        conn.commit()
        cur.close()
        conn.close()

        await query.answer(
            "✅ تم إعادة حسابك للمستوى الأول.",
            show_alert=True
        )
        return


# =========================================================
# التحكم بالأزرار
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    data = query.data

    # الإدارة
    if data.startswith("admin:"):
        await query.answer()

        await admin_button(
            query,
            context,
            data
        )
        return

    # الرئيسية
    if data == "home":
        await query.answer()

        await show_main_menu(
            update
        )
        return

    # مستوى مغلق
    if data.startswith("locked:"):

        await query.answer(
            "🔒 يجب النجاح في المستوى السابق أولاً.",
            show_alert=True
        )
        return

    # مستوى
    if data.startswith("level:"):

        await query.answer()

        try:
            level = int(
                data.split(":")[1]
            )
        except (
            ValueError,
            IndexError
        ):
            return

        await begin_level(
            query,
            context,
            level
        )
        return

    # إجابة
    if data.startswith("answer:"):

        await query.answer()

        try:
            correct = int(
                data.split(":")[1]
            )
        except (
            ValueError,
            IndexError
        ):
            return

        await answer_question(
            query,
            context,
            correct == 1
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
        CommandHandler(
            "admin",
            admin_panel
        )
    )

    app.add_handler(
        CommandHandler(
            "cancel",
            cancel
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # مهم:
    # يستقبل قوائم الأسئلة ورسائل الإدارة
    app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            admin_text_handler
        )
    )

    print(
        "5000 English Quiz Bot is running..."
    )

    app.run_polling()


if __name__ == "__main__":
    main()
