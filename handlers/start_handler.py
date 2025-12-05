# /root/NEURO_CHK/handlers/start_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from handlers.menu_handler import main_menu

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome *{user.first_name}*!\n\n"
        "🔮 *NeuroSnare Checker v6.3*\n"
        "Advanced card checking & authorization bot\n\n"
        "Use /menu to open main menu\n"
        "Use /help for commands list\n"
        "Use /credits to check your status\n\n"
        "*Features:*\n"
        "✅ Card checking\n"
        "✅ Multiple gateways\n"
        "✅ B3 Auth verification\n"
        "✅ Advanced tools\n"
        "✅ User management"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )
    
    # Show main menu after welcome
    await main_menu(update, context)

async def commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_message = (
        "📋 *Available Commands*\n\n"
        "*/start* - Start the bot\n"
        "*/menu* - Open main menu\n"
        "*/check* - Check NeuroSnare ID\n"
        "*/credits* - Check your credits\n"
        "*/help* - Show this message\n\n"
        "*Main Menu Options:*\n"
        "📊 Check NeuroSnare - Various checking methods\n"
        "🌐 Gateways - Payment gateways & B3 Auth\n"
        "⚡ Advance - Advanced tools\n"
        "👤 Credits - User information & status\n\n"
        "*B3 Auth Format:*\n"
        "`CARD|MM|YY|CVV`\n"
        "Example: `4111111111111111|12|25|123`"
    )
    
    await update.message.reply_text(
        help_message,
        parse_mode='Markdown'
    )

async def credits_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send credits information."""
    # This will be handled by menu_handler's credits section
    from handlers.menu_handler import button_handler
    
    # Create a fake callback query to trigger credits
    class FakeQuery:
        def __init__(self):
            self.data = "credits"
            self.message = update.message
    
    fake_update = Update(update.update_id + 1, message=update.message)
    fake_update.callback_query = FakeQuery()
    
    await button_handler(fake_update, context)