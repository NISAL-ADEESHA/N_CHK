# /root/NEURO_CHK/handlers/b3_handler.py
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from handlers.menu_handler import handle_b3_auth_card

async def b3_card_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle B3 Auth card input"""
    return await handle_b3_auth_card(update, context)

# In main.py, add:
# from handlers.b3_handler import b3_card_handler
# application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, b3_card_handler))