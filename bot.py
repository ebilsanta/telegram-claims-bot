import os
import logging
import database
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv 

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHOICE, ADD, REMOVE, CLEAR, DONE, VALIDATE = range(6)

def format_input_add(user_data):
	facts = [f"{key} - {value}" for key, value in user_data.items()]
	return "\n".join(facts).join(["\n", "\n"])

def format_result_view(results):
	index = 1
	output = ["These are your current claims:\n","    <b>Date</b>            <b>Desc</b>          <b>Amt</b>"]
	total = 0
	for row in results:
		date = row[1].__format__("%d/%m/%y")
		print(row[1])
		output.append(f"{str(index)}. {date} | {row[3]} | <b>${row[4]}</b>")
		total += row[4]
		index += 1
	output.append(f"\nTotal: <b>${total}</b>")
	return "\n".join(output)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens a the web app."""
    await update.message.reply_text(
        f"Hi {update.message.chat.username}! What would you like to do?",
        reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text="View claims"),
				KeyboardButton(text="Add claim")],
				[KeyboardButton(text="Remove claim"),
				KeyboardButton(text="Clear all claims")]
			],
			one_time_keyboard=True
		)
    )
    return CHOICE

async def view(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text("Give me a second now...")
	user_claims = database.get_claims(update.message.chat.username)
	print(type(user_claims))
	if isinstance(user_claims, str):
		await update.message.reply_text(
		f"{user_claims}"
    )
	else:
		format_claims = format_result_view(user_claims)
		await update.message.reply_text(
			f"{format_claims}",
			parse_mode="HTML"
		)
		user_claims.clear()
	return ConversationHandler.END

def valid_date(date_string):
	date_list = date_string.split('/')
	print(date_list)
	return len(date_list) == 2 and date_list[0].isnumeric() and date_list[1].isnumeric() and int(date_list[0]) < 32 and int(date_list[0]) > 0 and int(date_list[1]) > 0 and int(date_list[1]) < 13

async def add_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(
        "Please enter the date of the purchase (DD/MM)"
    )
	return ADD
	
async def add_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
	text = update.message.text
	print(text.split('/'))
	if not valid_date(text):
		await update.message.reply_text(
			"Please enter a valid date of purchase (DD/MM)"
		)
		return ADD
	context.user_data['Date'] = text
	await update.message.reply_text(
        "Please enter a short description of the purchase"
    )
	return ADD

async def add_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
	text = update.message.text
	context.user_data["Desc"] = text
	await update.message.reply_text(
        "Please enter the amount spent (without $)"
    )
	return ADD

async def add_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
	text = update.message.text
	context.user_data["Amount"] = text
	user_input = context.user_data
	await update.message.reply_text(
		f"I got this data from you: {format_input_add(user_input)}Would you like to confirm or restart?",
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text="Confirm"),
				KeyboardButton(text="Restart")],
			],
			one_time_keyboard=True
		)
    )
	return ADD

async def add_complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
	user_input = context.user_data
	await update.message.reply_text("Give me a second now...")
	success_message = database.add_claim(update.message.chat.username, user_input['Date'], user_input['Desc'], user_input['Amount'])
	user_claims = database.get_claims(update.message.chat.username)
	
	if isinstance(user_claims, str):
		await update.message.reply_text(
			"Unable to add or view current claims. Please contact @ebilsanta for help!"
		)
	else:
		format_claims = format_result_view(user_claims)
		await update.message.reply_text(
			f"{success_message}\n{format_claims}"
			, reply_markup=ReplyKeyboardRemove(),
			parse_mode='HTML'
		)
	user_input.clear()
	return ConversationHandler.END

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Give me a second now...")
    user_claims = database.get_claims(update.message.chat.username)
    format_claims = format_result_view(user_claims)
    await update.message.reply_text(
        f"{format_claims}\n\nWhich number would you like to remove? (eg. '1')",
		parse_mode='HTML'
    )
    return REMOVE

async def remove_complete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	await update.message.reply_text('Hang on there...')
	index = update.message.text
	success_message = database.delete_claim(update.message.chat.username, index)
	user_claims = database.get_claims(update.message.chat.username)
	format_claims = format_result_view(user_claims)
	await update.message.reply_text(
        f"{success_message}\n{format_claims}",
		parse_mode='HTML'
    )
	return ConversationHandler.END

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Give me a second now...")
    user_claims = database.get_claims(update.message.chat.username)
    format_claims = format_result_view(user_claims)
    await update.message.reply_text(
        f"These are the existing claims, are you sure you want to clear everything?\n{format_claims}",
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text="Yes"),
				KeyboardButton(text="Nope, cancel")],
			],
			one_time_keyboard=True
		),
		parse_mode='HTML'
    )
    return CLEAR

async def clear_complete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	database.clear_claims(update.message.chat.username)
	await update.message.reply_text(
        f"All claims cleared successfully."
    )
	return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
		text="Type /start to see options or type:\n'a' to add claim,\n'v' to view claims,\n'r' to remove claim,\n'c' to clear all claims.")


if __name__ == '__main__':
	application = ApplicationBuilder().token(os.getenv('BOT_TOKEN')).build()

	help_handler = CommandHandler("help", help)

	start_handler = ConversationHandler(
		entry_points=[CommandHandler("start", start),
						MessageHandler(filters.Regex("Add claim") | filters.Regex("add claim") |  filters.Regex("a"), add_date),
						MessageHandler(filters.Regex("View claims") | filters.Regex("view claim") | filters.Regex("v"), view),
						MessageHandler(filters.Regex("Remove claim") | filters.Regex("remove claim") | filters.Regex("r"), remove),
						MessageHandler(filters.Regex("Clear all claims") | filters.Regex("clear all claims") | filters.Regex("c"), clear)
					],
		states={
			CHOICE: [
				CommandHandler('start', start),
				MessageHandler(filters.Regex("Add claim"), add_date),
				MessageHandler(filters.Regex("View claims"), view),
				MessageHandler(filters.Regex("Remove claim"), remove),
				MessageHandler(filters.Regex("Clear all claims"), clear)
			],
			ADD: [	
				CommandHandler('start', start),
				MessageHandler(filters.Regex(r"/"), add_description),
				MessageHandler(filters.Regex("Restart"), add_date),
				MessageHandler(filters.Regex("Confirm"), add_complete),
				MessageHandler(filters.Regex("[^0-9/.]"), add_amount),
				MessageHandler(filters.Regex("[^a-zA-Z]") & filters.Regex("^((?!/).)*$"), add_confirm)
			],
			REMOVE: [
				CommandHandler('start', start),
				MessageHandler(filters.Regex("[0-9]"), remove_complete)
			],
			CLEAR: [
				CommandHandler('start', start),
				MessageHandler(filters.Regex("Yes"), clear_complete)
			],
		},
		fallbacks=[MessageHandler(filters.Regex("Done"), add_complete)]
	)

	application.add_handler(start_handler)

	application.run_polling()


