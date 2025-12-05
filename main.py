#!/usr/bin/env python3
# /root/NEURO_CHK/main.py
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.start_handler import start_command, commands_command, credits_check_command
from handlers.menu_handler import main_menu, button_handler, handle_b3_auth_card
from handlers.check_handler import neuro_check_command

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token (replace with your actual token)
TOKEN = "8366642226:AAHoWRCHfe1gCfYUszuNZPP-kx3D7_R48Sc"  # Replace with your bot token

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", commands_command))
    application.add_handler(CommandHandler("credits", credits_check_command))
    application.add_handler(CommandHandler("check", neuro_check_command))
    application.add_handler(CommandHandler("menu", main_menu))

    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_handler))

    # Add message handler for B3 Auth card input (MUST BE BEFORE other message handlers)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_b3_auth_card
    ))

    # Add message handler for other text messages
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the Bot
    print("🤖 Starting NeuroSnare Checker v6.3...")
    print("✅ Bot is running. Press Ctrl+C to stop.")
    
    # Run the bot until you press Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()