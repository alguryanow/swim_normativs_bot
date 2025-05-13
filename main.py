import logging
import os
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
    ["комплекс 100", "комплекс 200", "комплекс 400"], 
    ["спина 50", "спина 100", "спина 200"]
] 

headers = ['3ю', '2ю', '1ю', '3в', '2в', '1в', 'КМС', 'МС', 'МСМК']

male_25_data = {
    disciplines[0][0]: ["58.05", "48.05", "38.05", "33.05", "30.05", "26.95", "24.95", "23.95", "22.52"],
    disciplines[0][1]: ["02:01.10", "01:49.10", "01:30.10", "01:20.10", "01:10.10", "01:01.50", "58.00", "54.00", "50.15"],
    disciplines[0][2]: ["04:36.20", "03:56.20", "03:21.20", "02:57.20", "02:36.70", "02:17.95", "02:09.95", "02:02.95", "01:52.45"],
    disciplines[1][0]: ["01:05.05", "55.05", "45.05", "38.55", "35.05", "31.65", "30.00", "28.25", "26.28"],
    disciplines[1][1]: ["02:23.10", "02:03.10", "01:44.10", "01:28.10", "01:20.10", "01:11.40", "01:06.90", "01:03.00", "57.34"],
    disciplines[1][2]: ["05:04.60", "04:24.60", "03:51.60", "03:18.70", "02:55.70", "02:36.45", "02:26.45", "02:18.45", "02:05.56"],
    disciplines[2][0]: ["55.05", "45.05", "35.05", "29.05", "26.85", "24.45", "23.20", "22.45", "21.18"],
    disciplines[2][1]: ["02:03.10", "01:43.10", "01:23.10", "01:10.60", "01:03.10", "56.70", "53.30", "50.00", "46.72"],
    disciplines[2][2]: ["04:24.20", "03:45.00", "03:04.20", "02:38.70", "02:20.20", "02:05.70", "01:57.45", "01:50.95", "01:43.02"],
    disciplines[3][0]: ["08:29.00", "07:33.00", "06:37.00", "05:41.00", "05:00.00", "04:25.00", "04:08.50", "03:56.00", "03:40.94"],
    disciplines[3][1]: ["18:26.00", "16:26.00", "14:26.00", "12:24.00", "11:02.00", "09:24.00", "08:50.00", "08:17.00", "07:42.70"],
    disciplines[3][2]: ["35:30.00", "31:30.00", "27:30.00", "23:27.50", "20:27.50", "18:05.00", "17:06.50", "15:28.50", "14:44.74"],
    disciplines[4][0]: ["02:13.60", "01:53.60", "01:34.60", "01:23.60", "01:13.60", "01:05.50", "01:01.50", "56.50", "52.57"],
    disciplines[4][1]: ["04:44.20", "04:04.20", "03:29.20", "03:04.20", "02:38.95", "02:21.95", "02:14.45", "02:05.95", "01:54.17"],
    disciplines[4][2]: ["09:18.00", "08:22.00", "07:26.00", "06:31.00", "05:43.00", "05:02.00", "04:43.00", "04:28.00", "04:06.68"],
    disciplines[5][0]: ["01:01.55", "51.55", "41.55", "35.55", "32.05", "29.35", "27.35", "25.89", "23.29"],
    disciplines[5][1]: ["02:16.10", "01:56.10", "01:33.60", "01:21.10", "01:12.60", "01:04.40", "01:00.40", "57.00", "50.54"],
    disciplines[5][2]: ["04:50.20", "04:10.20", "03:24.20", "02:56.20", "02:36.20", "02:19.20", "02:11.45", "02:04.75", "01:52.45"]
}

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
        disciplines[4][1]: ["04:48.00", "04:08.00", "03:33.00", "03:08.00", "02:44.00", "02:25.75", "02:17.25", "02:09.75", "01:58.59"],
        disciplines[4][2]: ["09:24.00", "08:28.00", "07:32.00", "06:37.00", "05:48.00", "05:07.00", "04:48.00", "04:34.00", "04:13.76"],
        disciplines[5][0]: ["01:02.30", "52.30", "42.30", "36.30", "32.80", "29.95", "28.15", "26.65", "24.85"],
        disciplines[5][1]: ["02:17.60", "01:57.60", "01:35.10", "01:22.60", "01:14.10", "01:06.00", "01:02.00", "58.50", "53.72"],
        disciplines[5][2]: ["04:53.20", "04:13.20", "03:27.20", "02:59.20", "02:38.20", "02:22.45", "02:15.45", "02:07.75", "01:57.30"]
}

female_25_data = {
    disciplines[0][0]: ["01:03.55", "53.55", "43.55", "36.55", "33.55", "30.95", "28.45", "27.30", "25.62"],
    disciplines[0][1]: ["02:21.10", "02:01.10", "01:42.10", "01:30.10", "01:19.10", "01:09.50", "01:05.00", "01:01.50", "57.16"],
    disciplines[0][2]: ["05:01.20", "04:21.20", "03:45.20", "03:18.20", "02:55.20", "02:34.45", "02:24.45", "02:16.95", "02:07.15"],
    disciplines[1][0]: ["01:11.55", "01:01.55", "51.55", "44.05", "40.05", "35.95", "34.25", "32.45", "30.04"],
    disciplines[1][1]: ["02:37.10", "02:16.10", "02:06.10", "01:41.60", "01:29.60", "01:21.00", "01:16.00", "01:12.00", "01:05.05"],
    disciplines[1][2]: ["05:33.20", "04:51.60", "04:16.60", "03:39.60", "03:14.20", "02:53.95", "02:43.45", "02:34.45", "02:21.34"],
    disciplines[2][0]: ["59.05", "49.55", "39.55", "32.55", "30.55", "27.85", "26.55", "25.75", "24.13"],
    disciplines[2][1]: ["02:12.10", "01:53.10", "01:33.10", "01:19.10", "01:11.40", "01:03.84", "01:00.00", "56.00", "52.68"],
    disciplines[2][2]: ["04:43.20", "04:05.20", "03:25.20", "02:54.20", "02:36.20", "02:20.45", "02:11.75", "02:03.45", "01:55.02"],
    disciplines[3][0]: ["09:51.00", "08:40.00", "07:29.00", "06:18.00", "05:34.00", "04:52.00", "04:30.00", "04:20.00", "04:03.32"],
    disciplines[3][1]: ["21:00.00", "18:30.00", "16:00.00", "13:15.00", "11:42.00", "10:11.00", "09:30.00", "09:00.00", "08:23.99"],
    disciplines[3][2]: ["38:20.00", "34:10.00", "30:05.00", "25:57.50", "22:34.50", "20:04.50", "18:21.50", "17:12.50", "16:12.06"],
    disciplines[4][0]: ["02:45.60", "02:05.60", "01:46.60", "01:34.60", "01:23.60", "01:14.50", "01:09.50", "01:04.50", "59.56"],
    disciplines[4][1]: ["05:10.20", "04:30.20", "03:54.20", "03:25.20", "02:59.20", "02:38.95", "02:29.45", "02:20.95", "02:08.11"],
    disciplines[4][2]: ["10:37.00", "09:26.00", "08:15.00", "07:14.00", "06:21.00", "05:37.00", "05:15.50", "04:58.00", "04:35.03"],
    disciplines[5][0]: ["01:07.05", "57.05", "47.05", "40.55", "36.55", "31.55", "29.85", "28.65", "26.57"],
    disciplines[5][1]: ["02:28.10", "02:08.10", "01:45.10", "01:31.10", "01:21.10", "01:13.00", "01:08.50", "01:03.60", "57.36"],
    disciplines[5][2]: ["05:15.20", "04:35.20", "03:50.20", "03:16.20", "02:54.20", "02:34.95", "02:25.95", "02:17.95", "02:05.15"]
}

female_50_data = {
    disciplines[0][0]: ["01:04.30", "54.30", "44.30", "37.30", "34.30", "31.70", "29.20", "28.05", "26.03"],
    disciplines[0][1]: ["02:22.60", "02:02.60", "01:43.60", "01:31.60", "01:20.60", "01:11.00", "01:06.50", "01:03.00", "58.06"],
    disciplines[0][2]: ["05:04.20", "04:24.20", "03:48.20", "03:21.20", "02:58.20", "02:37.45", "02:27.45", "02:19.95", "02:08.90"],
    disciplines[1][0]: ["01:12.30", "01:02.30", "52.30", "44.80", "40.80", "36.70", "35.00", "33.20", "30.77"],
    disciplines[1][1]: ["02:38.60", "02:17.60", "02:07.60", "01:43.10", "01:31.10", "01:22.50", "01:17.50", "01:13.50", "01:06.88"],
    disciplines[1][2]: ["05:36.20", "04:54.20", "04:19.20", "03:42.20", "03:17.20", "02:56.95", "02:46.40", "02:37.45", "02:25.24"],
    disciplines[2][0]: ["59.80", "50.30", "40.30", "33.30", "31.30", "28.60", "27.30", "26.50", "24.82"],
    disciplines[2][1]: ["02:13.60", "01:54.60", "01:34.60", "01:20.60", "01:12.90", "01:05.34", "01:01.50", "57.50", "53.99"],
    disciplines[2][2]: ["04:46.20", "04:08.20", "03:28.20", "02:57.20", "02:38.20", "02:23.45", "02:14.76", "02:06.45", "01:56.90"],
    disciplines[3][0]: ["09:57.00", "08:46.00", "07:35.00", "06:24.00", "05:40.00", "04:59.00", "04:41.00", "04:26.00", "04:08.04"],
    disciplines[3][1]: ["21:12.00", "18:42.00", "16:12.00", "13:27.00", "11:54.00", "10:23.00", "09:42.00", "09:08.00", "08:31.12"],
    disciplines[3][2]: ["38:42.50", "34:32.50", "30:27.50", "26:20.00", "22:57.00", "20:27.00", "18:44.00", "17:35.00", "16:20.88"],
    disciplines[4][1]: ["05:14.00", "04:34.00", "03:58.00", "03:29.00", "03:03.00", "02:42.75", "02:33.25", "02:24.75", "02:12.12"],
    disciplines[4][2]: ["10:43.00", "09:32.00", "08:21.00", "07:20.00", "06:27.00", "05:42.00", "05:20.50", "05:03.00", "04:40.80"],
    disciplines[5][0]: ["01:07.80", "57.80", "47.80", "41.30", "37.30", "32.30", "30.70", "29.00", "28.05"],
    disciplines[5][1]: ["02:29.60", "02:09.60", "01:46.60", "01:32.60", "01:22.60", "01:14.50", "01:10.00", "01:06.00", "59.80"],
    disciplines[5][2]: ["05:18.00", "04:38.20", "03:53.20", "03:19.20", "02:57.20", "02:37.95", "02:28.95", "02:20.95", "02:09.77"]
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

    if pool == 25:
        if gender == 'Юноши':
            data = male_25_data[discipline]
        else:
            data = female_25_data[discipline]
    else:
        if gender == 'Юноши':
            data = male_50_data[discipline]
        else:
            data = female_50_data[discipline]

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

    # logger.info(f"{context.user_data=}")
    if context.user_data[POOL_LENGTH] == 50:
        if DISCIPLINE in context.user_data and context.user_data[DISCIPLINE] == 'комплекс 100':
            #-- для 50м бассейна нет норматива "комплекс 100"
            context.user_data[DISCIPLINE] = ''


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
    await query.answer()    # This acknowledges the button press
    
    data = query.data
    
    if data == "BTN_POOL":
        on_btn_pool_click(context)
    elif data == "BTN_GENDER":
        on_btn_gender_click(context)
    elif data == "BTN_DISCIPLINE_CURRENT":
        pass
    elif data.startswith("BTN_DISCIPLINE_NEW_"):
        new_discipline = data.split("_")[3]
        if new_discipline == 'комплекс 100':
            if POOL_LENGTH in context.user_data and context.user_data[POOL_LENGTH] == 50:
                await query.answer("Для бассейна 50 м нет норматива на 'комплекс 100'!", show_alert=True)  #--TODO: не работает
                return SELECTING_ACTION

        context.user_data[DISCIPLINE] = new_discipline

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
    application = Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    
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