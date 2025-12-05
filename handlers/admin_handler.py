from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.admin_utils import is_admin, promote_user, demote_user, get_admin_list
from utils.user_data import get_user_data, add_credits_to_user, save_user_data, load_user_data
from config import logger

async def promote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Promote user to admin (admin only)"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/promote <user_id>`")
        return
    
    try:
        target_user_id = int(context.args[0])
        
        if promote_user(target_user_id):
            user_data = get_user_data(target_user_id)
            user_data["is_admin"] = True
            save_user_data(load_user_data())
            
            await update.message.reply_text(
                f"✅ **User Promoted to Admin**\n\n"
                f"**User ID:** `{target_user_id}`\n"
                f"**Status:** 👑 ADMIN\n"
                f"**Permissions:** Full admin access\n\n"
                f"👨‍💻 *NeuroSnare Checker*",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text("❌ User is already an admin or promotion failed")
            
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
    except Exception as e:
        logger.error(f"Promote error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def demote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demote user from admin (admin only)"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/demote <user_id>`")
        return
    
    try:
        target_user_id = int(context.args[0])
        
        if demote_user(target_user_id):
            user_data = get_user_data(target_user_id)
            user_data["is_admin"] = False
            save_user_data(load_user_data())
            
            await update.message.reply_text(
                f"✅ **User Demoted to Regular User**\n\n"
                f"**User ID:** `{target_user_id}`\n"
                f"**Status:** 👤 USER\n"
                f"**Permissions:** Regular user access\n\n"
                f"👨‍💻 *NeuroSnare Checker*",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text("❌ Cannot demote initial admin or user not found")
            
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
    except Exception as e:
        logger.error(f"Demote error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of admins (admin only)"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    admins_list = get_admin_list()
    admin_text = "👑 **ADMIN LIST**\n\n"
    
    for i, admin_id in enumerate(admins_list, 1):
        admin_text += f"{i}. `{admin_id}`\n"
    
    admin_text += f"\n**Total Admins:** {len(admins_list)}\n\n👨‍💻 *NeuroSnare Checker*"
    
    await update.message.reply_text(admin_text, parse_mode=ParseMode.MARKDOWN)

async def add_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add credits to user (admin only)"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/addcredits <amount> <user_id>`\nExample: `/addcredits 500 1234567890`")
        return
    
    try:
        amount = int(context.args[0])
        target_user_id = int(context.args[1])
        
        if amount <= 0:
            await update.message.reply_text("❌ Amount must be positive")
            return
        
        new_credits = add_credits_to_user(target_user_id, amount)
        
        target_user_data = get_user_data(target_user_id)
        username = target_user_data.get("username", "Unknown")
        
        await update.message.reply_text(
            f"✅ **Credits Added Successfully**\n\n"
            f"**User ID:** `{target_user_id}`\n"
            f"**Username:** @{username}\n"
            f"**Credits Added:** {amount}\n"
            f"**New Total Credits:** {new_credits}\n\n"
            f"👨‍💻 *NeuroSnare Checker*",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except ValueError:
        await update.message.reply_text("❌ Invalid amount or user ID")
    except Exception as e:
        logger.error(f"Add credits error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")