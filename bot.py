import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation handler
QUESTION = 0

# Questions in Persian
questions = [
    {
        "text": "سؤال ۱: وقتی پول اضافی به دست می‌آورم، چه کار می‌کنم؟",
        "options": [
            {"text": "سریع خرج می‌کنم", "score": 1},
            {"text": "به خانواده یا دوستان قرض می‌دهم", "score": 2},
            {"text": "مقداری پس‌انداز می‌کنم", "score": 3},
            {"text": "به سرمایه‌گذاری فکر می‌کنم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۲: در مورد بودجه‌بندی ماهانه چه نظری دارید؟",
        "options": [
            {"text": "بودجه‌بندی را محدودیت می‌دانم", "score": 1},
            {"text": "گاهی بودجه‌بندی می‌کنم", "score": 2},
            {"text": "بودجه‌بندی می‌کنم اما انعطاف‌پذیر است", "score": 3},
            {"text": "بودجه‌بندی دقیق و منظم دارم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۳: در مورد بدهی‌های خود چه احساسی دارید؟",
        "options": [
            {"text": "بدهی را طبیعی می‌دانم و نگران نیستم", "score": 1},
            {"text": "سعی می‌کنم بدهی‌ها را مدیریت کنم", "score": 2},
            {"text": "برنامه‌ریزی برای پرداخت بدهی‌ها دارم", "score": 3},
            {"text": "تا حد ممکن از بدهی اجتناب می‌کنم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۴: در مورد پس‌انداز برای دوران بازنشستگی چه نظری دارید؟",
        "options": [
            {"text": "هنوز به آن فکر نکرده‌ام", "score": 1},
            {"text": "گاهی به آن فکر می‌کنم", "score": 2},
            {"text": "برنامه‌ای برای پس‌انداز بازنشستگی دارم", "score": 3},
            {"text": "به طور منظم برای بازنشستگی پس‌انداز می‌کنم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۵: در مورد سرمایه‌گذاری چه دیدگاهی دارید؟",
        "options": [
            {"text": "سرمایه‌گذاری را ریسک می‌دانم", "score": 1},
            {"text": "گاهی در مورد سرمایه‌گذاری تحقیق می‌کنم", "score": 2},
            {"text": "سرمایه‌گذاری‌های کوچک انجام می‌دهم", "score": 3},
            {"text": "سرمایه‌گذاری منظم و متنوع دارم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۶: در مورد بیمه‌های مختلف چه نظری دارید؟",
        "options": [
            {"text": "بیمه را هزینه اضافی می‌دانم", "score": 1},
            {"text": "فقط بیمه‌های اجباری را دارم", "score": 2},
            {"text": "چند بیمه مهم را دارم", "score": 3},
            {"text": "پوشش بیمه‌ای کامل دارم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۷: در مورد آموزش مالی چه نظری دارید؟",
        "options": [
            {"text": "نیازی به آموزش مالی نمی‌بینم", "score": 1},
            {"text": "گاهی مطالب مالی می‌خوانم", "score": 2},
            {"text": "به طور منظم در مورد مسائل مالی مطالعه می‌کنم", "score": 3},
            {"text": "در دوره‌های آموزشی مالی شرکت می‌کنم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۸: در مورد اهداف مالی بلندمدت چه نظری دارید؟",
        "options": [
            {"text": "اهداف مالی مشخصی ندارم", "score": 1},
            {"text": "گاهی به اهداف مالی فکر می‌کنم", "score": 2},
            {"text": "چند هدف مالی دارم", "score": 3},
            {"text": "اهداف مالی مشخص و برنامه‌ریزی شده دارم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۹: در مورد مدیریت ریسک مالی چه نظری دارید؟",
        "options": [
            {"text": "به ریسک مالی توجه نمی‌کنم", "score": 1},
            {"text": "گاهی به ریسک‌ها فکر می‌کنم", "score": 2},
            {"text": "سعی می‌کنم ریسک‌ها را مدیریت کنم", "score": 3},
            {"text": "استراتژی مدیریت ریسک دارم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۱۰: در مورد مشاوره مالی چه نظری دارید؟",
        "options": [
            {"text": "نیازی به مشاور مالی نمی‌بینم", "score": 1},
            {"text": "گاهی از دیگران مشورت می‌گیرم", "score": 2},
            {"text": "با مشاور مالی مشورت می‌کنم", "score": 3},
            {"text": "مشاور مالی ثابت دارم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۱۱: در مورد پس‌انداز برای مواقع اضطراری چه نظری دارید؟",
        "options": [
            {"text": "پس‌انداز اضطراری ندارم", "score": 1},
            {"text": "مقدار کمی پس‌انداز اضطراری دارم", "score": 2},
            {"text": "پس‌انداز اضطراری مناسبی دارم", "score": 3},
            {"text": "پس‌انداز اضطراری کامل دارم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۱۲: در مورد مدیریت هزینه‌های روزانه چه نظری دارید؟",
        "options": [
            {"text": "هزینه‌ها را کنترل نمی‌کنم", "score": 1},
            {"text": "گاهی هزینه‌ها را بررسی می‌کنم", "score": 2},
            {"text": "هزینه‌ها را مدیریت می‌کنم", "score": 3},
            {"text": "مدیریت دقیق هزینه‌ها دارم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۱۳: در مورد درآمدهای جانبی چه نظری دارید؟",
        "options": [
            {"text": "به درآمد جانبی فکر نمی‌کنم", "score": 1},
            {"text": "گاهی به درآمد جانبی فکر می‌کنم", "score": 2},
            {"text": "یک منبع درآمد جانبی دارم", "score": 3},
            {"text": "چند منبع درآمد متنوع دارم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۱۴: در مورد مالیات‌ها چه نظری دارید؟",
        "options": [
            {"text": "به مالیات توجه نمی‌کنم", "score": 1},
            {"text": "فقط مالیات‌های اجباری را می‌پردازم", "score": 2},
            {"text": "سعی می‌کنم مالیات‌ها را بهینه کنم", "score": 3},
            {"text": "برنامه‌ریزی مالیاتی دارم", "score": 4},
        ]
    },
    {
        "text": "سؤال ۱۵: در مورد میراث مالی چه نظری دارید؟",
        "options": [
            {"text": "به میراث مالی فکر نمی‌کنم", "score": 1},
            {"text": "گاهی به میراث مالی فکر می‌کنم", "score": 2},
            {"text": "برنامه‌ای برای میراث مالی دارم", "score": 3},
            {"text": "برنامه جامع میراث مالی دارم", "score": 4},
        ]
    }
]

# Advice mapping
advice_map = {
    (1, 1): "نیاز به بازنگری اساسی در باورهای مالی و خودکنترلی دارید.",
    (1, 2): "در مسیر خوبی هستید ولی باید آگاهی مالی‌تان را افزایش دهید.",
    (1, 3): "رفتار مالی نسبتاً سالمی دارید، اما هنوز جای رشد وجود دارد.",
    (1, 4): "طرز فکر مالی شما قوی است، آن را حفظ و تقویت کنید.",
    (2, 1): "بودجه‌بندی را به عنوان ابزاری برای آزادی مالی ببینید، نه محدودیت.",
    (2, 2): "بودجه‌بندی منظم می‌تواند به شما کمک کند تا اهداف مالی‌تان را بهتر مدیریت کنید.",
    (2, 3): "بودجه‌بندی انعطاف‌پذیر شما خوب است، اما سعی کنید منظم‌تر شوید.",
    (2, 4): "بودجه‌بندی دقیق شما عالی است، به همین روال ادامه دهید.",
    (3, 1): "بدهی می‌تواند مانع رشد مالی شما شود. سعی کنید آن را مدیریت کنید.",
    (3, 2): "مدیریت بدهی خوب است، اما برنامه‌ریزی برای کاهش آن را در نظر بگیرید.",
    (3, 3): "برنامه‌ریزی برای پرداخت بدهی‌ها عالی است، به آن پایبند باشید.",
    (3, 4): "اجتناب از بدهی غیرضروری عالی است، این رویکرد را حفظ کنید.",
    (4, 1): "هر چه زودتر برای بازنشستگی برنامه‌ریزی کنید، بهتر است.",
    (4, 2): "شروع به فکر کردن درباره بازنشستگی خوب است، حالا زمان عمل است.",
    (4, 3): "برنامه بازنشستگی شما خوب است، آن را منظم بررسی کنید.",
    (4, 4): "پس‌انداز منظم برای بازنشستگی عالی است، به همین روال ادامه دهید.",
    (5, 1): "سرمایه‌گذاری با ریسک همراه است، اما می‌تواند بازده خوبی داشته باشد.",
    (5, 2): "تحقیق درباره سرمایه‌گذاری خوب است، حالا زمان شروع است.",
    (5, 3): "سرمایه‌گذاری‌های کوچک شروع خوبی است، به تدریج گسترش دهید.",
    (5, 4): "سرمایه‌گذاری متنوع عالی است، به همین روال ادامه دهید.",
    (6, 1): "بیمه می‌تواند از دارایی‌های شما در برابر ریسک‌ها محافظت کند.",
    (6, 2): "بیمه‌های اجباری خوب است، اما پوشش بیشتری را در نظر بگیرید.",
    (6, 3): "پوشش بیمه‌ای شما خوب است، آن را منظم بررسی کنید.",
    (6, 4): "پوشش بیمه‌ای کامل عالی است، به همین روال ادامه دهید.",
    (7, 1): "آموزش مالی می‌تواند به شما کمک کند تا تصمیمات بهتری بگیرید.",
    (7, 2): "مطالعه مطالب مالی خوب است، آن را منظم‌تر کنید.",
    (7, 3): "مطالعه منظم مسائل مالی عالی است، به همین روال ادامه دهید.",
    (7, 4): "شرکت در دوره‌های آموزشی مالی عالی است، به یادگیری ادامه دهید.",
    (8, 1): "تعیین اهداف مالی می‌تواند به شما کمک کند تا بهتر برنامه‌ریزی کنید.",
    (8, 2): "فکر کردن به اهداف مالی خوب است، حالا زمان تعیین اهداف مشخص است.",
    (8, 3): "داشتن چند هدف مالی خوب است، آنها را اولویت‌بندی کنید.",
    (8, 4): "اهداف مالی مشخص و برنامه‌ریزی شده عالی است، به آنها پایبند باشید.",
    (9, 1): "مدیریت ریسک مالی می‌تواند از دارایی‌های شما محافظت کند.",
    (9, 2): "فکر کردن به ریسک‌ها خوب است، حالا زمان مدیریت آنهاست.",
    (9, 3): "مدیریت ریسک‌ها عالی است، آن را منظم بررسی کنید.",
    (9, 4): "استراتژی مدیریت ریسک عالی است، به همین روال ادامه دهید.",
    (10, 1): "مشاوره مالی می‌تواند به شما کمک کند تا تصمیمات بهتری بگیرید.",
    (10, 2): "مشورت با دیگران خوب است، اما مشاوره حرفه‌ای را در نظر بگیرید.",
    (10, 3): "مشورت با مشاور مالی عالی است، به این روال ادامه دهید.",
    (10, 4): "داشتن مشاور مالی ثابت عالی است، به این همکاری ادامه دهید.",
    (11, 1): "پس‌انداز اضطراری می‌تواند در مواقع بحرانی به شما کمک کند.",
    (11, 2): "پس‌انداز اضطراری کوچک شروع خوبی است، آن را افزایش دهید.",
    (11, 3): "پس‌انداز اضطراری مناسب عالی است، آن را حفظ کنید.",
    (11, 4): "پس‌انداز اضطراری کامل عالی است، به همین روال ادامه دهید.",
    (12, 1): "مدیریت هزینه‌ها می‌تواند به شما کمک کند تا پس‌انداز بیشتری داشته باشید.",
    (12, 2): "بررسی هزینه‌ها خوب است، حالا زمان مدیریت آنهاست.",
    (12, 3): "مدیریت هزینه‌ها عالی است، آن را منظم بررسی کنید.",
    (12, 4): "مدیریت دقیق هزینه‌ها عالی است، به همین روال ادامه دهید.",
    (13, 1): "درآمدهای جانبی می‌توانند به ثبات مالی شما کمک کنند.",
    (13, 2): "فکر کردن به درآمد جانبی خوب است، حالا زمان عمل است.",
    (13, 3): "داشتن یک منبع درآمد جانبی عالی است، به فکر گسترش آن باشید.",
    (13, 4): "چند منبع درآمد متنوع عالی است، به همین روال ادامه دهید.",
    (14, 1): "مدیریت مالیات می‌تواند به شما کمک کند تا هزینه‌های خود را کاهش دهید.",
    (14, 2): "پرداخت مالیات‌های اجباری خوب است، به فکر بهینه‌سازی باشید.",
    (14, 3): "بهینه‌سازی مالیات عالی است، آن را منظم بررسی کنید.",
    (14, 4): "برنامه‌ریزی مالیاتی عالی است، به همین روال ادامه دهید.",
    (15, 1): "برنامه‌ریزی میراث مالی می‌تواند به نسل‌های آینده کمک کند.",
    (15, 2): "فکر کردن به میراث مالی خوب است، حالا زمان برنامه‌ریزی است.",
    (15, 3): "برنامه میراث مالی عالی است، آن را منظم بررسی کنید.",
    (15, 4): "برنامه جامع میراث مالی عالی است، به همین روال ادامه دهید."
}

def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask the first question."""
    user = update.effective_user
    context.user_data['current_question'] = 0
    context.user_data['answers'] = []
    context.user_data['scores'] = []
    
    welcome_message = (
        f"سلام {user.first_name}! 👋\n\n"
        "به تست ذهنیت مالی خوش آمدید! 📊\n\n"
        "این تست شامل ۱۵ سؤال چند گزینه‌ای است که به شما کمک می‌کند "
        "ذهنیت مالی خود را بهتر بشناسید.\n\n"
        "لطفاً به هر سؤال با دقت پاسخ دهید.\n"
        "برای شروع، به سؤال اول پاسخ دهید:"
    )
    
    update.message.reply_text(welcome_message)
    return ask_question(update, context)

def ask_question(update: Update, context: CallbackContext) -> int:
    """Ask the current question."""
    current_question = context.user_data['current_question']
    
    if current_question >= len(questions):
        return show_results(update, context)
    
    question = questions[current_question]
    keyboard = []
    
    for i, option in enumerate(question['options']):
        keyboard.append([InlineKeyboardButton(option['text'], callback_data=str(i))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        update.callback_query.edit_message_text(
            text=question['text'],
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            text=question['text'],
            reply_markup=reply_markup
        )
    
    return QUESTION

def handle_answer(update: Update, context: CallbackContext) -> int:
    """Handle the user's answer and move to the next question."""
    query = update.callback_query
    query.answer()
    
    current_question = context.user_data['current_question']
    selected_option = int(query.data)
    
    # Store the answer and score
    context.user_data['answers'].append(selected_option)
    context.user_data['scores'].append(questions[current_question]['options'][selected_option]['score'])
    
    # Move to next question
    context.user_data['current_question'] += 1
    
    return ask_question(update, context)

def show_results(update: Update, context: CallbackContext) -> int:
    """Calculate and show the final results."""
    total_score = sum(context.user_data['scores'])
    
    # Determine the result category
    if total_score <= 29:
        category = "ضعیف – نیاز به آموزش فوری"
    elif total_score <= 44:
        category = "متوسط – نیاز به تقویت آگاهی"
    else:
        category = "خوب – ذهنیت مالی مناسب"
    
    # Prepare personalized advice
    advice = []
    for i, (question_num, answer) in enumerate(zip(range(1, len(questions) + 1), context.user_data['answers'])):
        advice.append(f"{i+1}. {advice_map.get((question_num, answer+1), '')}")
    
    # Send results
    result_message = (
        f"نتیجه تست ذهنیت مالی شما:\n\n"
        f"امتیاز کل: {total_score} از 60\n"
        f"دسته‌بندی: {category}\n\n"
        "توصیه‌های شخصی‌سازی شده:\n" +
        "\n".join(advice)
    )
    
    if update.callback_query:
        update.callback_query.edit_message_text(text=result_message)
    else:
        update.message.reply_text(text=result_message)
    
    return ConversationHandler.END

def main():
    """Start the bot."""
    # Get token from environment variable
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN environment variable is not set!")
    
    # Create the Updater and pass it your bot's token
    updater = Updater(token)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [CallbackQueryHandler(handle_answer)],
        },
        fallbacks=[],
    )
    
    dispatcher.add_handler(conv_handler)
    
    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
