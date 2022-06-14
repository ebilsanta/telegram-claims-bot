import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import os

PORT = int(os.environ.get('PORT', '5000'))

TOKEN = '5440405771:AAFEySa6ebHb0s64V_tQs8Ip2LntwnQtgpA'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.run_webhook(
		listen="0.0.0.0",
		port=int(PORT),
        url_path=TOKEN,
        webhook_url='https://telegram-claims-bot.herokuapp.com/' + TOKEN
    )



