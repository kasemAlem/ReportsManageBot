import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from commands import CommandHandler as BotCommandHandler, parse_command
from data_extraction import extract_data_from_message
from google_sheets import update_google_sheet, get_sheet_columns

# Initialize command handler
command_handler = BotCommandHandler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'Hi! I can help you update your Google Sheet. '
        'Send me data in the format: key1=value1, key2=value2\n\n'
        'Type /help to see available commands.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    message_text = update.message.text
    
    # Check if this is a command
    cmd, args, remaining_text = parse_command(message_text)
    if cmd:
        # Get sheet columns for context
        sheet_columns = await get_sheet_columns()
        cmd_context = {
            "platform": "telegram",
            "user": update.effective_user.username,
            "sheet_name": os.environ.get("SHEET_NAME", "Sheet1"),
            "sheet_columns": sheet_columns
        }
        
        response = await command_handler.handle_command(cmd, args, cmd_context)
        await update.message.reply_text(response)
        return
    
    # Process as data update
    extracted_data = extract_data_from_message(message_text)
    
    if not extracted_data:
        await update.message.reply_text(
            "I couldn't extract any data from your message. "
            "Please use the format: key1=value1, key2=value2\n"
            "Type /format to see examples."
        )
        return
    
    # Check if confirmation is required
    if os.environ.get("CONFIRMATION_REQUIRED", "False").lower() == "true":
        # Store the extracted data in user_data for confirmation
        context.user_data["pending_data"] = extracted_data
        
        # Build confirmation message
        confirm_msg = "I extracted the following data:\n"
        for key, value in extracted_data.items():
            confirm_msg += f"- {key}: {value}\n"
        confirm_msg += "\nShould I update the sheet? (yes/no)"
        
        await update.message.reply_text(confirm_msg)
    else:
        # Update Google Sheet directly
        success = await update_google_sheet(extracted_data)
        
        if success:
            await update.message.reply_text("Google Sheet updated successfully!")
        else:
            await update.message.reply_text("Failed to update Google Sheet. Please try again.")

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle confirmation responses."""
    if "pending_data" not in context.user_data:
        await update.message.reply_text("There's nothing to confirm.")
        return
    
    response = update.message.text.lower()
    if response in ["yes", "y"]:
        # Update Google Sheet with the stored data
        success = await update_google_sheet(context.user_data["pending_data"])
        
        if success:
            await update.message.reply_text("Google Sheet updated successfully!")
        else:
            await update.message.reply_text("Failed to update Google Sheet. Please try again.")
    else:
        await update.message.reply_text("Update cancelled.")
    
    # Clear the pending data
    del context.user_data["pending_data"]

def run_telegram_bot():
    """Run the Telegram bot."""
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    
    # Add command handlers for all registered commands
    for cmd in command_handler.commands:
        application.add_handler(CommandHandler(cmd, lambda update, context, cmd=cmd: 
            handle_command_wrapper(update, context, cmd)))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run the bot
    application.run_polling()

async def handle_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, cmd: str):
    """Wrapper for command handlers to use the CommandHandler class."""
    sheet_columns = await get_sheet_columns()
    cmd_context = {
        "platform": "telegram",
        "user": update.effective_user.username,
        "sheet_name": os.environ.get("SHEET_NAME", "Sheet1"),
        "sheet_columns": sheet_columns
    }
    
    response = await command_handler.handle_command(cmd, [], cmd_context)
    await update.message.reply_text(response)

if __name__ == "__main__":
    run_telegram_bot() 