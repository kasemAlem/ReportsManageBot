# ReportsManageBot

A flexible AI agent that connects WhatsApp and/or Telegram with Google Sheets, allowing users to update spreadsheet data directly from chat messages.

## 🌟 Features

- **Multi-Platform Support**: Works with both WhatsApp and Telegram
- **Natural Language Processing**: Extracts structured data from messages
- **Google Sheets Integration**: Automatically updates your spreadsheet
- **Command System**: Built-in commands for help, status, and more
- **Flexible Configuration**: Easy setup through environment variables
- **Confirmation System**: Optional confirmation before updating data

## 📋 Use Cases

- **Sales Reporting**: Field agents can report sales directly from their phones
- **Inventory Management**: Update stock levels on-the-go
- **Event Registration**: Collect participant information
- **Expense Tracking**: Log expenses as they occur
- **Data Collection**: Gather information from distributed teams

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- A Google account with access to Google Sheets
- For Telegram: A Telegram bot token (from [@BotFather](https://t.me/botfather))
- For WhatsApp: A Twilio account with WhatsApp API access

### Step-by-Step Installation Guide

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ReportsManageBot.git
cd ReportsManageBot
```

#### 2. Set Up a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# If you encounter Python environment errors (like "No module named 'encodings'"), try:
# This clears environment variables that might interfere with Python
env -i bash -c "unset PYTHONHOME PYTHONPATH && python3 -m venv venv"
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt

# You may want to update pip to the latest version
pip install --upgrade pip
```

#### 4. Set Up Google Sheets API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it
4. Create a service account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and click "Create"
   - Skip the optional steps and click "Done"
5. Create a key for your service account:
   - Click on the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON and click "Create"
   - The key file will be downloaded automatically
6. Rename the downloaded file to `sheet_credentials.json` and place it in the project root directory
7. Share your Google Sheet with the service account email (it looks like `name@project-id.iam.gserviceaccount.com`)

#### 5. Create Your Google Sheet

1. Create a new Google Sheet or use an existing one
2. Make sure the first row contains column headers (e.g., "product", "quantity", "price")
3. Note the Spreadsheet ID from the URL:
   - In `https://docs.google.com/spreadsheets/d/1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7/edit#gid=0`
   - The ID is `1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7`

#### 6. Configure Environment Variables

Run the setup script to configure your environment:

```bash
python setup.py
```

Follow the prompts to enter your:
- Telegram Bot Token (if using Telegram)
- Twilio credentials (if using WhatsApp)
- Google Spreadsheet ID
- Other configuration options

#### 7. For Telegram Bot Setup

1. Start a chat with [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions to create a new bot
3. Copy the API token provided by BotFather
4. Enter this token when prompted by the setup script

#### 8. For WhatsApp Bot Setup (via Twilio)

1. Sign up for a [Twilio account](https://www.twilio.com/try-twilio)
2. Navigate to the [WhatsApp sandbox](https://www.twilio.com/console/sms/whatsapp/sandbox)
3. Follow Twilio's instructions to connect your WhatsApp to the sandbox
4. Note your Account SID and Auth Token from the Twilio dashboard
5. Enter these credentials when prompted by the setup script

#### 9. Run the Bot

```bash
python main.py
```

The bot should now be running! If you're using WhatsApp, you'll need to expose your local server to the internet using a tool like [ngrok](https://ngrok.com/) and configure the Twilio webhook URL.

## 📱 Using the Bot

### Basic Usage

Send a message in this format to update your sheet: 

## 🔧 Troubleshooting

### Virtual Environment Issues

- **Error: No module named 'encodings'**: This usually happens when there's a conflict with Python environment variables. Use the alternative command provided in the installation steps that clears environment variables.

- **Command 'python' not found**: Try using `python3` instead of `python` on Linux/macOS systems.

- **Permission denied when activating virtual environment**: Make sure the activation script is executable with `chmod +x venv/bin/activate`.

### Google Sheets API Issues

- **"The caller does not have permission" error**: Make sure you've shared your Google Sheet with the service account email address.

- **Credentials not found**: Ensure your `sheet_credentials.json` file is in the project root directory and has the correct permissions.

### Messaging Platform Issues

- **Telegram bot not responding**: Check that your bot token is correct and that you've started a conversation with your bot.

- **WhatsApp messages not being received**: Verify your Twilio configuration and ensure your webhook URL is correctly set up and accessible from the internet.

If you encounter any other issues, please check the logs (`bot.log`) for more detailed error messages. 