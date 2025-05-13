import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states for conversation
SELECTING_ACTION = "SELECTING_ACTION"
SHOWING_RESULT = "SHOWING_RESULT"

# User data keys
POOL_LENGTH = "pool_length"
GENDER = "gender"
DISCIPLINE = "discipline"


disciplines = [
    ["батт 50", "батт 100", "батт 200"], 
    ["брасс 50", "брасс 100", "брасс 200"],
    ["кроль 50", "кроль 100", "кроль 200"],
    ["кроль 400", "кроль 800", "кроль 1500"],
    ["комплекс 200", "комплекс 400"], 
    ["спина 50", "спина 100", "спина 200"]
] 

headers = ['3ю', '2ю', '1ю', '3в', '2в', '1в', 'КМС', 'МС', 'МСМК']

male_50_data = {
        disciplines[0][0]: ["58.80", "48.80", "38.80", "33.80", "30.80", "27.70", "25.70", "24.70", "23.27"],
        disciplines[0][1]: ["02:10.60", "01:50.60", "01:31.60", "01:21.60", "01:11.60", "01:03.00", "59.50", "55.50", "51.62"],
        disciplines[0][2]: ["04:39.20", "03:59.20", "03:24.20", "03:00.20", "02:39.70", "02:20.95", "02:13.95", "02:05.95", "01:56.23"],
        disciplines[1][0]: ["01:05.80", "55.80", "45.80", "39.30", "35.80", "32.40", "30.50", "29.00", "27.22"],
        disciplines[1][1]: ["02:24.60", "02:04.60", "01:45.60", "01:29.60", "01:21.60", "01:13.00", "01:08.50", "01:04.50", "59.91"],
        disciplines[1][2]: ["05:07.20", "04:27.20", "03:54.20", "03:21.70", "02:58.70", "02:39.45", "02:29.45", "02:21.45", "02:09.97"],
        disciplines[2][0]: ["55.80", "45.80", "35.80", "29.80", "27.60", "25.20", "23.95", "23.20", "21.91"],
        disciplines[2][1]: ["02:04.60", "01:44.60", "01:24.60", "01:12.10", "01:04.60", "58.30", "54.90", "51.50", "48.25"],
        disciplines[2][2]: ["04:27.20", "03:47.20", "03:07.20", "02:41.70", "02:23.20", "02:08.95", "02:00.65", "01:53.95", "01:46.50"],
        disciplines[3][0]: ["08:35.00", "07:39.00", "06:43.00", "05:47.00", "05:06.00", "04:31.00", "04:14.50", "04:02.00", "03:47.71"],
        disciplines[3][1]: ["18:38.00", "16:38.00", "14:38.00", "12:36.00", "11:14.00", "09:37.00", "08:58.00", "08:25.00", "07:52.60"],
        disciplines[3][2]: ["35:52.50", "31:52.50", "27:52.00", "23:50.00", "20:50.00", "18:29.00", "17:29.00", "15:51.00", "15:06.19"],
        disciplines[4][0]: ["04:48.00", "04:08.00", "03:33.00", "03:08.00", "02:44.00", "02:25.75", "02:17.25", "02:09.75", "01:58.59"],
        disciplines[4][1]: ["09:24.00", "08:28.00", "07:32.00", "06:37.00", "05:48.00", "05:07.00", "04:48.00", "04:34.00", "04:13.76"],
        disciplines[5][0]: ["01:02.30", "52.30", "42.30", "36.30", "32.80", "29.95", "28.15", "26.65", "24.85"],
        disciplines[5][1]: ["02:17.60", "01:57.60", "01:35.10", "01:22.60", "01:14.10", "01:06.00", "01:02.00", "58.50", "53.72"],
        disciplines[5][2]: ["04:53.20", "04:13.20", "03:27.20", "02:59.20", "02:38.20", "02:22.45", "02:15.45", "02:07.75", "01:57.30"]
}

START_MSG = "Добро пожаловать в таблицу разрядов по плаванию! \nВыберите длину бассейна, пол и дисциплину:"

def get_result(user_data):
    """Get result based on user selections."""
    pool = user_data.get(POOL_LENGTH)
    gender = user_data.get(GENDER)
    discipline = user_data.get(DISCIPLINE)
    
    if not all([pool, gender, discipline]):
        return None
    
    result = f"Бассейн {pool}м, {gender},\n{discipline}:\n\n"

    data = male_50_data[discipline]
    result += "`   3ю-1ю: " + '   '.join(data[0:3]) + '`\n'
    result += "`   3в-1в: " + '   '.join(data[3:6]) + '`\n'
    result += "`КМС-МСМК: " + '   '.join(data[6:9]) + '`\n'
    
    return result

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Start the conversation and display buttons for the first selection."""
    # Initialize user data if needed
    context.user_data.clear()
    
    await update.message.reply_text(
        START_MSG,
        reply_markup=get_selection_keyboard(context.user_data)
    )
    
    return SELECTING_ACTION

def get_selection_keyboard(user_data):
    """Create an inline keyboard based on the current selections."""
    buttons = []
    
    # Pool length selection
    pool_text = f"Бассейн (25м/50м): {user_data.get(POOL_LENGTH, 'Не выбран')}"
    buttons.append([InlineKeyboardButton(text=pool_text, callback_data="BTN_POOL")])
    
    # Gender selection
    gender_text = f"Пол (Юноши/Девушки): {user_data.get(GENDER, 'Не выбран')}"
    buttons.append([InlineKeyboardButton(text=gender_text, callback_data="BTN_GENDER")])
    
    # Discipline selection
    # discipline_text = f"Дисциплина: {user_data.get(DISCIPLINE, 'Не выбрана')}"
    # buttons.append([InlineKeyboardButton(text=discipline_text, callback_data="BTN_DISCIPLINE_CURRENT")])
    
    # Create buttons for each discipline
    for subdisc in disciplines:
        row = []
        for discipline in subdisc:
            btn_text = discipline
            if DISCIPLINE in user_data and user_data[DISCIPLINE] == discipline:
                btn_text = '✅' + btn_text
            row.append(InlineKeyboardButton(btn_text, callback_data=f"BTN_DISCIPLINE_NEW_{discipline}"))
        buttons.append(row)
       
    return InlineKeyboardMarkup(buttons)

def on_btn_pool_click(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle BTN_POOL click """

    current_selection = context.user_data.get(POOL_LENGTH, None)
    if current_selection is None:
        context.user_data[POOL_LENGTH] = 25
    elif current_selection == 25:
        context.user_data[POOL_LENGTH] = 50
    else:
        context.user_data[POOL_LENGTH] = 25


def on_btn_gender_click(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle BTN_GENDER click"""
    
    current_selection = context.user_data.get(GENDER, None)
    if current_selection is None:
        context.user_data[GENDER] = 'Юноши'
    elif current_selection == 'Юноши':
        context.user_data[GENDER] = 'Девушки'
    else:
        context.user_data[GENDER] = 'Юноши'


async def handle_btn_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle button click"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "BTN_POOL":
        on_btn_pool_click(context)
    elif data == "BTN_GENDER":
        on_btn_gender_click(context)
    elif data == "BTN_DISCIPLINE_CURRENT":
        pass
    elif data.startswith("BTN_DISCIPLINE_NEW_"):
        # Remove the DISCIPLINE_ prefix
        context.user_data[DISCIPLINE] = data.split("_")[3]

    result = get_result(context.user_data)
    if result is not None:
        reply_text = result
    else:
        reply_text = START_MSG

    await query.edit_message_text(
        text=reply_text, 
        parse_mode="Markdown",
        reply_markup=get_selection_keyboard(context.user_data)
    )

    return SELECTING_ACTION

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(text="Thank you for using the Swimming Records Bot!")
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Application
    application = Application.builder().token("7605949549:AAGnZXZmNXaUpyL9AnvSFr_NjybKdsFnkkQ").build()
    
    # Load data from file
    # global swim_data
    # swim_data = load_data_from_file("your_data_file.txt")
    
    # Setup conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(handle_btn_click),
            ],
        },
        fallbacks=[CommandHandler("end", end)],
    )
    
    # Add ConversationHandler to application
    application.add_handler(conv_handler)
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()