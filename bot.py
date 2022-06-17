import os
import logging
import database
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

PORT = int(os.environ.get('PORT', '8443'))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHOICE, VIEW, ADD, REMOVE, CLEAR, DONE = range(6)

def format_input_add(user_data):
	facts = [f"{key} - {value}" for key, value in user_data.items()]
	return "\n".join(facts).join(["\n", "\n"])

def format_result_view(results):
	index = 1
	output = ["No. Date  Desc   Amt"]
	total = 0
	for row in results:
		date = row[1].__format__("%d/%m")
		output.append(f"{str(index)}. {date}  {row[3]}   ${row[4]}")
		total += row[4]
		index += 1
	output.append(f"Total: ${total}")
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
	user_claims = database.get_claims(update.message.chat.username)
	if isinstance(user_claims, str):
		await update.message.reply_text(
		f"{user_claims}"
    )
	else:
		format_claims = format_result_view(user_claims)
		await update.message.reply_text(
			f"{format_claims}"
		)
		user_claims.clear()
	return ConversationHandler.END


async def add_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(
        "Please enter the day of the purchase (DD/MM)"
    )
	return ADD
	
async def add_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
	text = update.message.text
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
	success_message = database.add_claim(update.message.chat.username, user_input['Date'], user_input['Desc'], user_input['Amount'])
	user_claims = database.get_claims(update.message.chat.username)
	if isinstance(user_claims, str):
		await update.message.reply_text(
			"Unable to add or view current claims. Please contact @ebilsanta for help!"
		)
	else:
		format_claims = format_result_view(user_claims)
		await update.message.reply_text(
			f"{success_message}\nThese are your current claims:\n{format_claims}"
			, reply_markup=ReplyKeyboardRemove()
		)
	user_input.clear()
	return ConversationHandler.END

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_claims = database.get_claims(update.message.chat.username)
    format_claims = format_result_view(user_claims)
    await update.message.reply_text(
        f"These are the existing claims, which number would you like to remove?\n{format_claims}"
    )
    return REMOVE

async def remove_complete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	index = update.message.text
	success_message = database.delete_claim(update.message.chat.username, index)
	user_claims = database.get_claims(update.message.chat.username)
	format_claims = format_result_view(user_claims)
	await update.message.reply_text(
        f"{success_message} These are the existing claims.\n{format_claims}"
    )
	return ConversationHandler.END

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
		)
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


if __name__ == '__main__':
	application = ApplicationBuilder().token(os.environ['BOT_TOKEN']).build()

	start_handler = ConversationHandler(
		entry_points=[CommandHandler("start", start),
						MessageHandler(filters.Regex("Add claim"), add_date),
						MessageHandler(filters.Regex("View claims"), view),
						MessageHandler(filters.Regex("Remove claim"), remove),
						MessageHandler(filters.Regex("Clear all claims"), clear)
					],
		states={
			CHOICE: [
				MessageHandler(filters.Regex("Add claim"), add_date),
				MessageHandler(filters.Regex("View claims"), view),
				MessageHandler(filters.Regex("Remove claim"), remove),
				MessageHandler(filters.Regex("Clear all claims"), clear)

			],
			ADD: [	
				MessageHandler(filters.Regex(r"/"), add_description),
				MessageHandler(filters.Regex("Restart"), add_date),
				MessageHandler(filters.Regex("Confirm"), add_complete),
				MessageHandler(filters.Regex("[^0-9/.]"), add_amount),
				MessageHandler(filters.Regex("[^a-zA-Z]") & filters.Regex("^((?!/).)*$"), add_confirm)
			],
			REMOVE: [
				MessageHandler(filters.Regex("[0-9]"), remove_complete)
			],
			CLEAR: [
				MessageHandler(filters.Regex("Yes"), clear_complete)
			]
		},
		fallbacks=[MessageHandler(filters.Regex("Done"), add_complete)]
	)

	application.add_handler(start_handler)

	application.run_webhook(
		listen='0.0.0.0',
		port=os.environ['PORT'],
		url_path=os.environ['BOT_TOKEN'],
		webhook_url='https://telegram-claims-bot.herokuapp.com/' + os.environ['BOT_TOKEN']
	)


