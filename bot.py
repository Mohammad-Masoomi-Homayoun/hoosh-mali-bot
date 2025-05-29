import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Configure logging with more detailed format
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Changed to DEBUG for more detailed logs
)
logger = logging.getLogger(__name__)

# Read token from environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN")
logger.debug(f"Environment variables available: {dict(os.environ)}")
logger.debug(f"TELEGRAM_TOKEN value: {'Set' if TOKEN else 'Not set'}")

if not TOKEN:
    logger.error("TELEGRAM_TOKEN environment variable is not set!")
    raise ValueError("TELEGRAM_TOKEN environment variable is not set!")
else:
    logger.info("Telegram token loaded successfully")

# Function to respond to messages
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message:
            user = update.message.from_user
            logger.info(f"Received message from user {user.id} ({user.first_name}): {update.message.text}")
            response = f"شما نوشتید: {update.message.text}"
            await update.message.reply_text(response)
            logger.info(f"Sent response to user {user.id}")
    except Exception as e:
        logger.error(f"Error in echo handler: {str(e)}", exc_info=True)

# Main function
def main():
    try:
        logger.info("Starting bot...")
        app = ApplicationBuilder().token(TOKEN).build()
        logger.info("Application built successfully")
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        logger.info("Message handler added successfully")
        
        logger.info("Starting polling...")
        app.run_polling()
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
