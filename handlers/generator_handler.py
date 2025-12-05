import os
import time
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.card_generator import generate_random_cc, create_cc_file, parse_card_parameters
from datetime import datetime

async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dual Function Card Generation"""
    if not context.args:
        await update.message.reply_text(
            "❌ **Dual Function Card Generator**\n\n"
            "**Format 1 - Simple BIN:**\n"
            "`/gen 410621000768 10` - 10 cards with this BIN\n"
            "`/gen 511111 20` - 20 MasterCard cards\n\n"
            "**Format 2 - Full Parameters:**\n"
            "`/gen 410621000768|08|2028 5` - 5 cards with specific date\n"
            "`/gen 410621000768|08|2028|123 5` - With date & CVV\n"
            "`/gen 410621000768|123 10` - With CVV only\n\n"
            "**Parameters:**\n"
            "• BIN: 6-19 digits (can be partial card number)\n"
            "• Amount: 1-1000 (default: 10)\n"
            "• Format: BIN|MM|YYYY|CVV (any part optional)\n"
            "• Example: `/gen 410621000768|08|28` - 10 cards with month 08, year 2028"
        )
        return
    
    input_str = context.args[0]
    amount = 10
    
    if len(context.args) > 1:
        try:
            amount = int(context.args[1])
            if amount > 1000:
                amount = 1000
            if amount < 1:
                amount = 1
        except ValueError:
            await update.message.reply_text("❌ Amount must be a number")
            return
    
    bin_pattern, exp_month, exp_year, cvv = parse_card_parameters(input_str)
    
    if not bin_pattern or not bin_pattern.isdigit():
        await update.message.reply_text("❌ BIN must contain only digits")
        return
    
    bin_length = len(bin_pattern)
    if bin_length < 6 or bin_length > 19:
        await update.message.reply_text(f"❌ BIN must be 6-19 digits (got {bin_length})")
        return
    
    if exp_month:
        try:
            exp_month = int(exp_month)
            if not (1 <= exp_month <= 12):
                await update.message.reply_text("❌ Month must be between 01-12")
                return
        except (ValueError, TypeError):
            await update.message.reply_text("❌ Month must be a number (01-12)")
            return
    
    if exp_year:
        try:
            if exp_year < 100:
                current_year = datetime.now().year
                century = current_year // 100 ** 100
                exp_year = century + exp_year
                if exp_year < current_year:
                    exp_year += 100
            elif exp_year < 2000 or exp_year > 2100:
                await update.message.reply_text("❌ Year must be between 2000-2100")
                return
        except (ValueError, TypeError):
            await update.message.reply_text("❌ Year must be a number")
            return
    
    if cvv:
        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            await update.message.reply_text("❌ CVV must be 3 or 4 digits")
            return
    
    processing_msg = await update.message.reply_text(f"⏳ Generating {amount} cards...")
    
    try:
        cards = generate_random_cc(bin_pattern, amount, exp_month, exp_year, cvv)
        
        param_info = f"**Parameters:**\n• BIN: `{bin_pattern}`\n• Amount: {amount}"
        if exp_month:
            param_info += f"\n• Month: {exp_month:02d}"
        if exp_year:
            param_info += f"\n• Year: {exp_year}"
        if cvv:
            param_info += f"\n• CVV: {cvv}"
        
        if amount <= 10:
            message = f"**🔧 Generated Cards**\n\n{param_info}\n\n"
            for i, card in enumerate(cards, 1):
                message += f"`{card}`\n"
            message += f"\n👨‍💻 **NeuroSnare Checker**"
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            if amount > 5:
                filename = create_cc_file(cards, f"cc_{bin_pattern}_{int(time.time())}.txt")
                with open(filename, 'rb') as file:
                    await update.message.reply_document(
                        document=file,
                        filename=filename,
                        caption=f"📁 Generated {amount} cards\n{param_info}\n\n💡 **Tip:** Reply to this file with `/st1m` to check all cards!",
                        parse_mode=ParseMode.MARKDOWN
                    )
                os.remove(filename)
                
        else:
            filename = create_cc_file(cards, f"cc_{bin_pattern}_{int(time.time())}.txt")
            with open(filename, 'rb') as file:
                await update.message.reply_document(
                    document=file,
                    filename=filename,
                    caption=f"📁 Generated {amount} cards\n{param_info}\n\n💡 **Tip:** Reply to this file with `/st1m` to check all cards!\n\n👨‍💻 **NeuroSnare Checker**",
                    parse_mode=ParseMode.MARKDOWN
                )
            os.remove(filename)
        
        await processing_msg.delete()
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating cards: {str(e)}")