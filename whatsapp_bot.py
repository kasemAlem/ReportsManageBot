from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from commands import CommandHandler as BotCommandHandler, parse_command
from data_extraction import extract_data_from_message
from google_sheets import update_google_sheet, get_sheet_columns
import re
from typing import Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
from telegram_bot import run_telegram_bot

app = Flask(__name__)

# Initialize command handler
command_handler = BotCommandHandler()

# Store pending confirmations (in a real app, use a database)
pending_confirmations = {}

@app.route("/whatsapp", methods=["POST"])
async def whatsapp_webhook():
    # Get the message and sender
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    
    # Create response
    resp = MessagingResponse()
    
    # Check if this is a confirmation response
    if sender in pending_confirmations:
        response = incoming_msg.lower()
        if response in ["yes", "y"]:
            # Update Google Sheet with the stored data
            success = await update_google_sheet(pending_confirmations[sender])
            
            if success:
                resp.message("Google Sheet updated successfully!")
            else:
                resp.message("Failed to update Google Sheet. Please try again.")
        else:
            resp.message("Update cancelled.")
        
        # Clear the pending confirmation
        del pending_confirmations[sender]
        return str(resp)
    
    # Check if this is a command
    cmd, args, remaining_text = parse_command(incoming_msg)
    if cmd:
        # Get sheet columns for context
        sheet_columns = await get_sheet_columns()
        cmd_context = {
            "platform": "whatsapp",
            "user": sender,
            "sheet_name": os.environ.get("SHEET_NAME", "Sheet1"),
            "sheet_columns": sheet_columns
        }
        
        response = await command_handler.handle_command(cmd, args, cmd_context)
        resp.message(response)
        return str(resp)
    
    # Process as data update
    extracted_data = extract_data_from_message(incoming_msg)
    
    if not extracted_data:
        resp.message(
            "I couldn't extract any data from your message. "
            "Please use the format: key1=value1, key2=value2\n"
            "Type /format to see examples."
        )
        return str(resp)
    
    # Check if confirmation is required
    if os.environ.get("CONFIRMATION_REQUIRED", "False").lower() == "true":
        # Store the extracted data for confirmation
        pending_confirmations[sender] = extracted_data
        
        # Build confirmation message
        confirm_msg = "I extracted the following data:\n"
        for key, value in extracted_data.items():
            confirm_msg += f"- {key}: {value}\n"
        confirm_msg += "\nShould I update the sheet? (yes/no)"
        
        resp.message(confirm_msg)
    else:
        # Update Google Sheet directly
        success = await update_google_sheet(extracted_data)
        
        if success:
            resp.message("Google Sheet updated successfully!")
        else:
            resp.message("Failed to update Google Sheet. Please try again.")
    
    return str(resp)

def run_whatsapp_bot():
    """Run the WhatsApp bot."""
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG_MODE", "True").lower() == "true"
    
    app.run(host=host, port=port, debug=debug)

def extract_data_from_message(message: str) -> Optional[Dict[str, Any]]:
    """
    Extract structured data from a message.
    
    Example message: "Update sales report: product=Laptop, quantity=5, price=1200"
    """
    # You can use regex patterns to extract key-value pairs
    pattern = r'(\w+)=([^,]+)'
    matches = re.findall(pattern, message)
    
    if not matches:
        return None
    
    # Convert matches to dictionary
    extracted_data = {key.strip(): value.strip() for key, value in matches}
    
    # You can add additional processing here, like type conversion
    # For example, convert numeric values from strings to numbers
    for key in extracted_data:
        if extracted_data[key].isdigit():
            extracted_data[key] = int(extracted_data[key])
        elif extracted_data[key].replace('.', '', 1).isdigit():
            extracted_data[key] = float(extracted_data[key])
    
    return extracted_data

def update_google_sheet(data: Optional[Dict[str, Any]]) -> bool:
    """
    Update Google Sheet with the extracted data.
    Returns True if successful, False otherwise.
    """
    if not data:
        return False
    
    try:
        # Set up credentials
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'sheet_credentials.json'  # Your service account credentials
        SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')  # Your spreadsheet ID
        SHEET_NAME = os.environ.get('SHEET_NAME', 'Sheet1')  # Sheet name
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        service = build('sheets', 'v4', credentials=credentials)
        sheets = service.spreadsheets()
        
        # First, get the headers to know which columns to update
        result = sheets.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1:Z1"
        ).execute()
        headers = result.get('values', [[]])[0]
        
        # Find the next empty row
        result = sheets.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:A"
        ).execute()
        rows = result.get('values', [])
        next_row = len(rows) + 1
        
        # Prepare the row data based on headers
        row_data = []
        for header in headers:
            if header in data:
                row_data.append(data[header])
            else:
                row_data.append("")
        
        # Update the sheet
        sheets.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A{next_row}",
            valueInputOption="USER_ENTERED",
            body={"values": [row_data]}
        ).execute()
        
        return True
    
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        return False

# Load environment variables
load_dotenv()

# Choose which platform to run (or run both)
PLATFORM = os.environ.get("PLATFORM", "telegram").lower()  # "telegram", "whatsapp", or "both"

if __name__ == "__main__":
    if PLATFORM == "telegram" or PLATFORM == "both":
        run_telegram_bot(extract_data_from_message, update_google_sheet)
    
    if PLATFORM == "whatsapp" or PLATFORM == "both":
        run_whatsapp_bot() 