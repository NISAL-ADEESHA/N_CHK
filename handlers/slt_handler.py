import time
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.user_data import get_user_data, update_slt_stats
from utils.admin_utils import is_admin
from config import logger
from gateways.slt_checker import SLTChecker

async def slt_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check single card on SLT gateway (Admin only)"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ This command is for admins only!")
        return
    
    username = update.effective_user.username or "N/A"
    user_data = get_user_data(user_id, username)
    
    if not context.args:
        await update.message.reply_text(
            "❌ **SLT Mastercard Checker (Admin Only)**\n\n"
            "**Usage:** `/slt CC|MM|YY|CVV [amount]`\n"
            "**Example:** `/slt 4111111111111111|12|25|123 100.50`\n\n"
            "**Parameters:**\n"
            "• Card: CC|MM|YY|CVV format\n"
            "• Amount: Optional LKR amount (default: 100.00)\n"
            "**Credits:** 0 credits for admins"
        )
        return

    card = context.args[0]
    amount = 100.0
    
    if len(context.args) > 1:
        try:
            amount = float(context.args[1])
            if amount <= 0:
                amount = 100.0
        except ValueError:
            amount = 100.0

    try:
        cc, mm, yy, cvv = card.split("|")
    except:
        await update.message.reply_text("❌ Invalid card format. Use: CC|MM|YY|CVV")
        return

    msg = await update.message.reply_text(f"🔍 Checking card on SLT Mastercard gateway...\n💰 Amount: LKR {amount:.2f}")

    # Update SLT check count
    update_slt_stats(user_id, "check")
    
    start = time.time()
    result = SLTChecker.test_card(card, amount)
    t = round(time.time() - start, 2)

    if result["status"] == "Approved":
        update_slt_stats(user_id, "approved", True)
        
        txt = (
            f"**🏦 SLT MASTERCARD - APPROVED ✅**\n\n"
            f"**Card:** `{card}`\n"
            f"**Amount:** LKR {result['amount']:.2f}\n"
            f"**Gateway:** {result['gateway']}\n"
            f"**Response:** {result['message']}\n"
            f"**Response Code:** {result.get('response_code', 'N/A')}\n"
            f"**Brand:** {result.get('brand', 'N/A')}\n"
            f"**Type:** {result.get('type', 'N/A')}\n"
            f"**Country:** {result.get('country', 'N/A')}\n"
            f"**BIN:** {result.get('bin', 'N/A')}\n"
            f"**Bank:** {result.get('bank', 'N/A')}\n"
            f"**Time:** {t}s\n\n"
            f"👑 Admin: Unlimited Credits\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
    elif result["status"] == "Declined":
        txt = (
            f"**🏦 SLT MASTERCARD - DECLINED ❌**\n\n"
            f"**Card:** `{card}`\n"
            f"**Amount:** LKR {result['amount']:.2f}\n"
            f"**Gateway:** {result['gateway']}\n"
            f"**Response:** {result['message']}\n"
            f"**Response Code:** {result.get('response_code', 'N/A')}\n"
            f"**Brand:** {result.get('brand', 'N/A')}\n"
            f"**Type:** {result.get('type', 'N/A')}\n"
            f"**Country:** {result.get('country', 'N/A')}\n"
            f"**BIN:** {result.get('bin', 'N/A')}\n"
            f"**Bank:** {result.get('bank', 'N/A')}\n"
            f"**Time:** {t}s\n\n"
            f"👑 Admin: Unlimited Credits\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
    else:
        txt = (
            f"**🏦 SLT MASTERCARD - ERROR ⚠️**\n\n"
            f"**Card:** `{card}`\n"
            f"**Error:** {result['message']}\n"
            f"**Time:** {t}s\n\n"
            f"👑 Admin: Unlimited Credits\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )

    await msg.edit_text(txt, parse_mode=ParseMode.MARKDOWN)

async def slt_mass_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mass check cards on SLT gateway (Admin only)"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ This command is for admins only!")
        return
    
    username = update.effective_user.username or "N/A"
    user_data = get_user_data(user_id, username)
    
    if not context.args:
        await update.message.reply_text(
            "❌ **SLT Mass Check (Admin Only)**\n\n"
            "**Usage:** `/sltm CC|MM|YY|CVV CC|MM|YY|CVV ...`\n"
            "**Example:** `/sltm 4111111111111111|12|25|123 5111111111111111|06|26|456`\n\n"
            "**Parameters:**\n"
            "• Multiple cards separated by spaces\n"
            "• Each card: CC|MM|YY|CVV format\n"
            "• Amount: LKR 100.00 (fixed)\n"
            "**Credits:** 0 credits for admins"
        )
        return
    
    cards = context.args
    amount = 100.0

    processing_msg = await update.message.reply_text(f"🔍 Processing {len(cards)} cards on SLT gateway...")

    # Update SLT check count
    update_slt_stats(user_id, "check")

    results_text = f"**🏦 SLT MASTERCARD MASS CHECK**\n💰 Amount: LKR {amount:.2f}\n👑 Admin Mode\n\n"
    approved_count = 0
    declined_count = 0
    error_count = 0
    live_cards = []

    for i, card in enumerate(cards, 1):
        try:
            cc, mm, yy, cvv = card.split("|")
            if len(cc) < 15 or len(cc) > 16 or not cc.isdigit():
                results_text += f"❌ Invalid Card `{card}`\n\n"
                error_count += 1
                continue
        except:
            results_text += f"❌ Invalid Format `{card}`\n\n"
            error_count += 1
            continue

        start = time.time()
        result = SLTChecker.test_card(card, amount)
        t = round(time.time() - start, 2)

        if result["status"] == "Approved":
            results_text += f"✅ **APPROVED** `{card}`\n"
            results_text += f"   Response: {result['message']} | Time: {t}s\n\n"
            approved_count += 1
            live_cards.append(card)
        elif result["status"] == "Declined":
            results_text += f"❌ **DECLINED** `{card}`\n"
            results_text += f"   Reason: {result['message']} | Time: {t}s\n\n"
            declined_count += 1
        else:
            results_text += f"⚠️ **ERROR** `{card}`\n"
            results_text += f"   Error: {result['message']}\n\n"
            error_count += 1

        if i % 3 == 0:
            progress = f"🔄 Processing: {i}/{len(cards)} cards..."
            await processing_msg.edit_text(progress)
        await asyncio.sleep(0.3)

    if approved_count > 0:
        update_slt_stats(user_id, "approved", True)

    results_text += (
        f"📊 **SUMMARY**\n"
        f"✅ Approved: {approved_count}\n"
        f"❌ Declined: {declined_count}\n"
        f"⚠️ Errors: {error_count}\n"
        f"📋 Total: {len(cards)} cards\n"
        f"🏦 Gateway: SLT Mastercard\n"
        f"💎 Credits used: 0 (Admin)\n"
        f"💎 Credits left: ♾️ Unlimited\n\n"
    )

    if live_cards:
        results_text += f"💳 **LIVE CARDS ({len(live_cards)})**\n"
        for card in live_cards[:10]:
            results_text += f"`{card}`\n"
        if len(live_cards) > 10:
            results_text += f"... and {len(live_cards) - 10} more\n"
        results_text += "\n"

    results_text += f"👨‍💻 *NeuroSnare Checker*"

    if len(results_text) > 4000:
        parts = [results_text[i:i+4000] for i in range(0, len(results_text), 4000)]
        for part in parts:
            await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
        await processing_msg.delete()
    else:
        await processing_msg.edit_text(results_text, parse_mode=ParseMode.MARKDOWN)