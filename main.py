#!/usr/bin/env python3
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
if os.path.exists("user.env"):
    load_dotenv("user.env")
else:
    print("Warning: user.env file not found. Run setup.py to create it.")
    load_dotenv()  # Try to load from .env as fallback

# Configure logging
log_level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO"))
log_file = os.environ.get("LOG_FILE", "bot.log")

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = []
    
    platform = os.environ.get("PLATFORM", "both").lower()
    
    if platform in ["telegram", "both"]:
        required_vars.append("TELEGRAM_BOT_TOKEN")
    
    if platform in ["whatsapp", "both"]:
        required_vars.extend([
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER"
        ])
    
    required_vars.extend([
        "SPREADSHEET_ID",
        "SHEET_NAME"
    ])
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please run setup.py to configure your environment.")
        return False
    
    return True

def main():
    """Main function to run the bot."""
    logger.info("Starting ReportsManageBot")
    
    if not check_environment():
        sys.exit(1)
    
    platform = os.environ.get("PLATFORM", "both").lower()
    
    if platform in ["telegram", "both"]:
        try:
            from telegram_bot import run_telegram_bot
            import threading
            logger.info("Starting Telegram bot")
            telegram_thread = threading.Thread(target=run_telegram_bot)
            telegram_thread.daemon = True
            telegram_thread.start()
        except ImportError:
            logger.error("Failed to import telegram_bot. Make sure python-telegram-bot is installed.")
            if platform == "telegram":
                sys.exit(1)
    
    if platform in ["whatsapp", "both"]:
        try:
            from whatsapp_bot import run_whatsapp_bot
            logger.info("Starting WhatsApp bot")
            run_whatsapp_bot()  # This will block as it runs a Flask server
        except ImportError:
            logger.error("Failed to import whatsapp_bot. Make sure Flask and Twilio are installed.")
            if platform == "whatsapp":
                sys.exit(1)
    
    # If we're only running Telegram, we need to keep the main thread alive
    if platform == "telegram":
        import time
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main() 