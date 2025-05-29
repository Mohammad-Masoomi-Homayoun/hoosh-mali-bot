import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

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
def echo(update: Update, context: CallbackContext):
    try:
        if update.message:
            user = update.message.from_user
            logger.info(f"Received message from user {user.id} ({user.first_name}): {update.message.text}")
            response = f"شما نوشتید: {update.message.text}"
            update.message.reply_text(response)
            logger.info(f"Sent response to user {user.id}")
    except Exception as e:
        logger.error(f"Error in echo handler: {str(e)}", exc_info=True)

# Main function
def main():
    try:
        logger.info("Starting bot...")
        updater = Updater(TOKEN)
        logger.info("Updater created successfully")
        
        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher
        
        # Add message handler
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
        logger.info("Message handler added successfully")
        
        # Start the Bot
        logger.info("Starting polling...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
