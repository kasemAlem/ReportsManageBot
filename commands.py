from typing import Dict, Any, Callable, List, Tuple

class CommandHandler:
    """Handler for bot commands."""
    
    def __init__(self):
        self.commands = {}
        self.register_default_commands()
    
    def register_command(self, command: str, handler: Callable, description: str):
        """Register a new command with its handler and description."""
        self.commands[command] = (handler, description)
    
    def register_default_commands(self):
        """Register default commands."""
        self.register_command("help", self.help_command, "Show available commands")
        self.register_command("status", self.status_command, "Check bot status")
        self.register_command("format", self.format_command, "Show message format examples")
        self.register_command("columns", self.columns_command, "Show available columns in the sheet")
    
    async def handle_command(self, command: str, args: List[str], context: Dict[str, Any]) -> str:
        """Handle a command and return the response."""
        if command in self.commands:
            handler, _ = self.commands[command]
            return await handler(args, context)
        return f"Unknown command: {command}. Type /help to see available commands."
    
    async def help_command(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle the help command."""
        help_text = "Available commands:\n\n"
        for cmd, (_, desc) in self.commands.items():
            help_text += f"/{cmd} - {desc}\n"
        return help_text
    
    async def status_command(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle the status command."""
        sheet_name = context.get("sheet_name", "Unknown")
        platform = context.get("platform", "Unknown")
        return f"Bot Status: Online\nPlatform: {platform}\nConnected to sheet: {sheet_name}"
    
    async def format_command(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle the format command."""
        return (
            "Message Format Examples:\n\n"
            "1. Simple key-value pairs:\n"
            "   product=Laptop, quantity=5, price=1200\n\n"
            "2. With a command prefix:\n"
            "   /update product=Laptop, quantity=5, price=1200\n\n"
            "3. Natural language (if advanced NLP is enabled):\n"
            "   Please update the sales record for Laptop with 5 units at $1200 each"
        )
    
    async def columns_command(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle the columns command."""
        columns = context.get("sheet_columns", [])
        if not columns:
            return "Unable to retrieve sheet columns. Please check your Google Sheets connection."
        
        return "Available columns in the sheet:\n" + "\n".join([f"- {col}" for col in columns])

# Function to parse commands from messages
def parse_command(message: str) -> Tuple[str, List[str], str]:
    """
    Parse a command from a message.
    Returns (command, args, remaining_text)
    """
    if not message.startswith('/'):
        return "", [], message
    
    # Split the message into parts
    parts = message.split(' ', 1)
    command = parts[0][1:].lower()  # Remove the / and convert to lowercase
    
    remaining_text = parts[1] if len(parts) > 1 else ""
    args = remaining_text.split() if remaining_text else []
    
    return command, args, remaining_text 