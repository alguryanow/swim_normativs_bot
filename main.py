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

# Sample data - in a real application, this would be loaded from your text file
def load_data_from_file(filename):
    # Implement your file reading logic here
    # Return data in a structured format
    return {}

# Sample data structure - replace with your file reading function
swim_data = {}

def get_result(user_data):
    """Get result based on user selections."""
    pool = user_data.get(POOL_LENGTH)
    gender = user_data.get(GENDER)
    discipline = user_data.get(DISCIPLINE)
    
    if not all([pool, gender, discipline]):
        return "Please complete all selections first."
    
    # In a real application, you would fetch the appropriate data here
    # For example: result = swim_data.get(pool, {}).get(gender, {}).get(event, "No data found")
    result = f"Result for {pool}m pool, {gender}, {discipline}"

    swimming_data = {
            "50, баттерфляй": ["58.80", "48.80", "38.80", "33.80", "30.80", "27.70", "25.70", "24.70", "23.27"],
            "100, баттерфляй": ["02:10.60", "01:50.60", "01:31.60", "01:21.60", "01:11.60", "01:03.00", "59.50", "55.50", "51.62"],
            "200, баттерфляй": ["04:39.20", "03:59.20", "03:24.20", "03:00.20", "02:39.70", "02:20.95", "02:13.95", "02:05.95", "01:56.23"],
            "50, брасс": ["01:05.80", "55.80", "45.80", "39.30", "35.80", "32.40", "30.50", "29.00", "27.22"],
            "100, брасс": ["02:24.60", "02:04.60", "01:45.60", "01:29.60", "01:21.60", "01:13.00", "01:08.50", "01:04.50", "59.91"],
            "200, брасс": ["05:07.20", "04:27.20", "03:54.20", "03:21.70", "02:58.70", "02:39.45", "02:29.45", "02:21.45", "02:09.97"],
            "50, вольный стиль": ["55.80", "45.80", "35.80", "29.80", "27.60", "25.20", "23.95", "23.20", "21.91"],
            "100, вольный стиль": ["02:04.60", "01:44.60", "01:24.60", "01:12.10", "01:04.60", "58.30", "54.90", "51.50", "48.25"],
            "200, вольный стиль": ["04:27.20", "03:47.20", "03:07.20", "02:41.70", "02:23.20", "02:08.95", "02:00.65", "01:53.95", "01:46.50"],
            "400, вольный стиль": ["08:35.00", "07:39.00", "06:43.00", "05:47.00", "05:06.00", "04:31.00", "04:14.50", "04:02.00", "03:47.71"],
            "800, вольный стиль": ["18:38.00", "16:38.00", "14:38.00", "12:36.00", "11:14.00", "09:37.00", "08:58.00", "08:25.00", "07:52.60"],
            "1500, вольный стиль": ["35:52.50", "31:52.50", "27:52.00", "23:50.00", "20:50.00", "18:29.00", "17:29.00", "15:51.00", "15:06.19"],
            "200, комплекс": ["04:48.00", "04:08.00", "03:33.00", "03:08.00", "02:44.00", "02:25.75", "02:17.25", "02:09.75", "01:58.59"],
            "400, комплекс": ["09:24.00", "08:28.00", "07:32.00", "06:37.00", "05:48.00", "05:07.00", "04:48.00", "04:34.00", "04:13.76"],
            "50, на спине": ["01:02.30", "52.30", "42.30", "36.30", "32.80", "29.95", "28.15", "26.65", "24.85"],
            "100, на спине": ["02:17.60", "01:57.60", "01:35.10", "01:22.60", "01:14.10", "01:06.00", "01:02.00", "58.50", "53.72"],
            "200, на спине": ["04:53.20", "04:13.20", "03:27.20", "02:59.20", "02:38.20", "02:22.45", "02:15.45", "02:07.75", "01:57.30"]
    }

    return result + "\n\n" + str(swimming_data[discipline])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Start the conversation and display buttons for the first selection."""
    # Initialize user data if needed
    context.user_data.clear()
    
    await update.message.reply_text(
        "Добро пожаловать в таблицу разрядов по плаванию! \nВыберите длину бассейна, пол и дисциплину:",
        reply_markup=get_selection_keyboard(context.user_data)
    )
    
    return SELECTING_ACTION

def get_selection_keyboard(user_data):
    """Create an inline keyboard based on the current selections."""
    buttons = []
    
    # Pool length selection
    pool_text = f"Бассейн (25м/50м): {user_data.get(POOL_LENGTH, 'Не выбран')}"
    buttons.append([InlineKeyboardButton(text=pool_text, callback_data="CHOOSE_POOL")])
    
    # Gender selection
    gender_text = f"Пол (Юноши/Девушки): {user_data.get(GENDER, 'Не выбран')}"
    buttons.append([InlineKeyboardButton(text=gender_text, callback_data="CHOOSE_GENDER")])
    
    # Discipline selection
    discipline_text = f"Дисциплина: {user_data.get(DISCIPLINE, 'Не выбрана')}"
    buttons.append([InlineKeyboardButton(text=discipline_text, callback_data="CHOOSE_DISCIPLINE")])
    
    # Show result button (if all selections are made)
    if all([POOL_LENGTH in user_data, GENDER in user_data, DISCIPLINE in user_data]):
        buttons.append([InlineKeyboardButton(text="Show Result", callback_data="SHOW_RESULT")])
    
    return InlineKeyboardMarkup(buttons)

async def select_pool(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle pool length selection."""
    query = update.callback_query
    await query.answer()
    

    current_selection = context.user_data.get(POOL_LENGTH, None)
    if current_selection is None:
        context.user_data[POOL_LENGTH] = 25
    elif current_selection == 25:
        context.user_data[POOL_LENGTH] = 50
    else:
        context.user_data[POOL_LENGTH] = 25
    
    reply_markup=get_selection_keyboard(context.user_data)

    await query.edit_message_text(
        text="Continue:", reply_markup=reply_markup
    )


    return SELECTING_ACTION

async def select_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle gender selection."""
    query = update.callback_query
    await query.answer()
    
    current_selection = context.user_data.get(GENDER, None)
    if current_selection is None:
        context.user_data[GENDER] = 'Юноши'
    elif current_selection == 'Юноши':
        context.user_data[GENDER] = 'Девушки'
    else:
        context.user_data[GENDER] = 'Юноши'
    
    reply_markup=get_selection_keyboard(context.user_data)

    await query.edit_message_text(
        text="Continue:", reply_markup=reply_markup
    )
    
    return SELECTING_ACTION

async def select_discipline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle discipline selection."""
    query = update.callback_query
    await query.answer()
    
    # This would normally be loaded from your database
    disciplines = [
        ["батт 50", "батт 100", "батт 200"], 
        ["брасс 50", "брасс 100", "брасс 200"],
        ["кроль 50", "кроль 100", "кроль 200"],
        ["кроль 400", "кроль 800", "кроль 1500"],
        ["комплекс 200", "комплекс 400"], 
        ["спина 50", "спина 100", "спина 200"]
    ] 
    
    keyboard = []
    # Create buttons for each discipline
    for subdisc in disciplines:
        row = []
        for discipline in subdisc:
            btn_text = discipline
            if DISCIPLINE in context.user_data and context.user_data[DISCIPLINE] == discipline:
                btn_text = '✅' + btn_text
            row.append(InlineKeyboardButton(btn_text, callback_data=f"DISCIPLINE_{discipline}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("Back", callback_data="BACK_TO_MENU")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="Select discipline:", reply_markup=reply_markup
    )
    
    return SELECTING_ACTION

async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle button selection."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("POOL_"):
        context.user_data[POOL_LENGTH] = data.split("_")[1] + "m"
        await query.edit_message_text(
            text="Please continue with your selections:",
            reply_markup=get_selection_keyboard(context.user_data)
        )
    elif data.startswith("GENDER_"):
        context.user_data[GENDER] = data.split("_")[1]
        await query.edit_message_text(
            text="Please continue with your selections:",
            reply_markup=get_selection_keyboard(context.user_data)
        )
    elif data.startswith("DISCIPLINE_"):
        # Remove the DISCIPLINE_ prefix
        context.user_data[DISCIPLINE] = data.split("_")[1]
        await query.edit_message_text(
            text="Please continue with your selections:",
            reply_markup=get_selection_keyboard(context.user_data)
        )
    
    return SELECTING_ACTION

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Show the result based on selections."""
    query = update.callback_query
    await query.answer()
    
    result = get_result(context.user_data)
    
    keyboard = [[InlineKeyboardButton("Back to Selections", callback_data="BACK_TO_MENU")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"{result}",
        reply_markup=reply_markup
    )
    
    return SELECTING_ACTION

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Return to the main menu."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="Please make your selections:",
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
                CallbackQueryHandler(select_pool, pattern="^CHOOSE_POOL$"),
                CallbackQueryHandler(select_gender, pattern="^CHOOSE_GENDER$"),
                CallbackQueryHandler(select_discipline, pattern="^CHOOSE_DISCIPLINE$"),
                CallbackQueryHandler(show_result, pattern="^SHOW_RESULT$"),
                CallbackQueryHandler(back_to_menu, pattern="^BACK_TO_MENU$"),
                CallbackQueryHandler(handle_selection, pattern="^(POOL_|GENDER_|DISCIPLINE_)"),
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