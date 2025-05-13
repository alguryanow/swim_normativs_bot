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
EVENT = "event"

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
    event = user_data.get(EVENT)
    
    if not all([pool, gender, event]):
        return "Please complete all selections first."
    
    # In a real application, you would fetch the appropriate data here
    # For example: result = swim_data.get(pool, {}).get(gender, {}).get(event, "No data found")
    result = f"Result for {pool}m pool, {gender}, {event}"
    return result

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Start the conversation and display buttons for the first selection."""
    # Initialize user data if needed
    context.user_data.clear()
    
    await update.message.reply_text(
        "Welcome to the Swimming Records Bot! Please make your selections:",
        reply_markup=get_selection_keyboard(context.user_data)
    )
    
    return SELECTING_ACTION

def get_selection_keyboard(user_data):
    """Create an inline keyboard based on the current selections."""
    buttons = []
    
    # Pool length selection
    pool_text = f"Pool: {user_data.get(POOL_LENGTH, 'Not selected')}"
    buttons.append([InlineKeyboardButton(text=pool_text, callback_data="CHOOSE_POOL")])
    
    # Gender selection
    gender_text = f"Gender: {user_data.get(GENDER, 'Not selected')}"
    buttons.append([InlineKeyboardButton(text=gender_text, callback_data="CHOOSE_GENDER")])
    
    # Event selection
    event_text = f"Event: {user_data.get(EVENT, 'Not selected')}"
    buttons.append([InlineKeyboardButton(text=event_text, callback_data="CHOOSE_EVENT")])
    
    # Show result button (if all selections are made)
    if all([POOL_LENGTH in user_data, GENDER in user_data, EVENT in user_data]):
        buttons.append([InlineKeyboardButton(text="Show Result", callback_data="SHOW_RESULT")])
    
    return InlineKeyboardMarkup(buttons)

async def select_pool(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle pool length selection."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("25m", callback_data=f"POOL_25"),
            InlineKeyboardButton("50m", callback_data=f"POOL_50"),
        ],
        [InlineKeyboardButton("Back", callback_data="BACK_TO_MENU")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="Select pool length:", reply_markup=reply_markup
    )
    
    return SELECTING_ACTION

async def select_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle gender selection."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("Female", callback_data=f"GENDER_Female"),
            InlineKeyboardButton("Male", callback_data=f"GENDER_Male"),
        ],
        [InlineKeyboardButton("Back", callback_data="BACK_TO_MENU")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="Select gender:", reply_markup=reply_markup
    )
    
    return SELECTING_ACTION

async def select_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle event selection."""
    query = update.callback_query
    await query.answer()
    
    # This would normally be loaded from your database
    events = [
        "50m Freestyle", "100m Freestyle", "200m Freestyle", 
        "50m Backstroke", "100m Backstroke", "200m Backstroke",
        "50m Breaststroke", "100m Breaststroke", "200m Breaststroke",
        "50m Butterfly", "100m Butterfly", "200m Butterfly",
        "200m Individual Medley", "400m Individual Medley"
    ]
    
    keyboard = []
    # Create buttons for each event, 2 per row
    for i in range(0, len(events), 2):
        row = []
        row.append(InlineKeyboardButton(events[i], callback_data=f"EVENT_{events[i]}"))
        if i + 1 < len(events):
            row.append(InlineKeyboardButton(events[i+1], callback_data=f"EVENT_{events[i+1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("Back", callback_data="BACK_TO_MENU")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="Select event:", reply_markup=reply_markup
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
    elif data.startswith("EVENT_"):
        # Remove the EVENT_ prefix
        context.user_data[EVENT] = data[6:]
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
                CallbackQueryHandler(select_event, pattern="^CHOOSE_EVENT$"),
                CallbackQueryHandler(show_result, pattern="^SHOW_RESULT$"),
                CallbackQueryHandler(back_to_menu, pattern="^BACK_TO_MENU$"),
                CallbackQueryHandler(handle_selection, pattern="^(POOL_|GENDER_|EVENT_)"),
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