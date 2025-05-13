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

# Define conversation states
POOL_LENGTH, GENDER, SWIM_STYLE = range(3)

# Sample swimming styles/distances - replace with your actual options
SWIM_STYLES = [
    "50m Freestyle", "100m Freestyle", "200m Freestyle", "400m Freestyle", "800m Freestyle", "1500m Freestyle",
    "50m Backstroke", "100m Backstroke", "200m Backstroke",
    "50m Breaststroke", "100m Breaststroke", "200m Breaststroke",
    "50m Butterfly", "100m Butterfly", "200m Butterfly",
    "200m Individual Medley", "400m Individual Medley"
]

# Function to read data from text file
def read_data_from_file(pool_length, gender, swim_style):
    """Read and return data from your text file based on selections"""
    # This is where you would implement your file reading logic
    # For example:
    # with open('swimming_data.txt', 'r') as f:
    #     data = f.readlines()
    # 
    # Filter data based on pool_length, gender, swim_style
    # Return the filtered data
    
    # Placeholder return:
    return f"Data for {pool_length}m pool, {gender}, {swim_style}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for pool length."""
    keyboard = [
        [
            InlineKeyboardButton("25m", callback_data="25"),
            InlineKeyboardButton("50m", callback_data="50"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to the Swimming Database Bot! Please select pool length:",
        reply_markup=reply_markup,
    )
    return POOL_LENGTH

async def pool_length(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the pool length and ask for gender."""
    query = update.callback_query
    await query.answer()
    
    context.user_data["pool_length"] = query.data
    
    keyboard = [
        [
            InlineKeyboardButton("Female", callback_data="female"),
            InlineKeyboardButton("Male", callback_data="male"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"Pool length: {query.data}m\nPlease select gender:",
        reply_markup=reply_markup,
    )
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the gender and ask for swimming style/distance."""
    query = update.callback_query
    await query.answer()
    
    context.user_data["gender"] = query.data
    
    # Create a keyboard with swim styles (multiple rows due to many options)
    keyboard = []
    row = []
    for i, style in enumerate(SWIM_STYLES):
        row.append(InlineKeyboardButton(style, callback_data=style))
        if (i + 1) % 2 == 0 or i == len(SWIM_STYLES) - 1:  # 2 buttons per row
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"Pool length: {context.user_data['pool_length']}m\nGender: {query.data}\nPlease select swimming style and distance:",
        reply_markup=reply_markup,
    )
    return SWIM_STYLE

async def swim_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show the data based on all selections."""
    query = update.callback_query
    await query.answer()
    
    context.user_data["swim_style"] = query.data
    
    # Retrieve data from file
    pool_length = context.user_data["pool_length"]
    gender = context.user_data["gender"]
    swim_style = context.user_data["swim_style"]
    
    data = read_data_from_file(pool_length, gender, swim_style)
    
    await query.edit_message_text(
        text=f"Pool length: {pool_length}m\nGender: {gender}\nEvent: {swim_style}\n\n{data}\n\nUse /start to search again."
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text("Search canceled. Use /start to begin a new search.")
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Application
    application = Application.builder().token("7605949549:AAGnZXZmNXaUpyL9AnvSFr_NjybKdsFnkkQ").build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            POOL_LENGTH: [CallbackQueryHandler(pool_length)],
            GENDER: [CallbackQueryHandler(gender)],
            SWIM_STYLE: [CallbackQueryHandler(swim_style)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()