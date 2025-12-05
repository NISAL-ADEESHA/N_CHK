import json
import os
from datetime import datetime
from config import USER_DATA_FILE, ADMINS_FILE, ADMIN_IDS, DAILY_CREDITS
from utils.admin_utils import is_admin

def load_user_data():
    """Load user data from file"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        from config import logger
        logger.error(f"Error loading user data: {e}")
    return {}

def save_user_data(user_data):
    """Save user data to file"""
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(user_data, f, indent=2)
    except Exception as e:
        from config import logger
        logger.error(f"Error saving user data: {e}")

def get_user_data(user_id, username=""):
    """Get or create user data"""
    user_data = load_user_data()
    user_id_str = str(user_id)
    
    if user_id_str not in user_data:
        user_data[user_id_str] = {
            "user_id": user_id,
            "username": username,
            "credits": DAILY_CREDITS,
            "last_daily": datetime.now().strftime('%Y-%m-%d'),
            "total_checked": 0,
            "approved_cards": 0,
            "join_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "is_admin": is_admin(user_id),
            "plan": "FREE",
            "daily_reset": True,
            "slt_checks": 0,
            "slt_approved": 0,
            "carnage_checks": 0,
            "carnage_approved": 0,
            "cg_checks": 0,
            "cg_approved": 0
        }
        save_user_data(user_data)
        return user_data[user_id_str]
    
    user = user_data[user_id_str]
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user.get("last_daily") != today:
        user["credits"] = DAILY_CREDITS
        user["last_daily"] = today
        user["daily_reset"] = True
        save_user_data(user_data)
        from config import logger
        logger.info(f"🔄 Daily credits reset for user {user_id}: {DAILY_CREDITS} credits")
    
    user["is_admin"] = is_admin(user_id)
    return user

def update_user_credits(user_id, credits_used):
    """Update user credits after usage"""
    user_data = load_user_data()
    user_id_str = str(user_id)
    
    if user_id_str in user_data:
        user_data[user_id_str]["credits"] -= credits_used
        user_data[user_id_str]["total_checked"] += credits_used
        save_user_data(user_data)
        return user_data[user_id_str]["credits"]
    return 0

def update_approved_cards(user_id, count=1):
    """Update approved cards count"""
    user_data = load_user_data()
    user_id_str = str(user_id)
    
    if user_id_str in user_data:
        user_data[user_id_str]["approved_cards"] += count
        save_user_data(user_data)

def add_credits_to_user(user_id, credits):
    """Add credits to user account"""
    user_data = load_user_data()
    user_id_str = str(user_id)
    
    if user_id_str not in user_data:
        user_data[user_id_str] = {
            "user_id": user_id,
            "username": "Unknown",
            "credits": credits,
            "last_daily": datetime.now().strftime('%Y-%m-%d'),
            "total_checked": 0,
            "approved_cards": 0,
            "join_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "is_admin": is_admin(user_id),
            "plan": "FREE",
            "daily_reset": True,
            "slt_checks": 0,
            "slt_approved": 0,
            "carnage_checks": 0,
            "carnage_approved": 0,
            "cg_checks": 0,
            "cg_approved": 0
        }
    else:
        user_data[user_id_str]["credits"] += credits
    
    save_user_data(user_data)
    from config import logger
    logger.info(f"💰 Added {credits} credits to user {user_id}. Total: {user_data[user_id_str]['credits']}")
    return user_data[user_id_str]["credits"]

def update_cg_stats(user_id, check_type="check", approved=False):
    """Update CG donation checker statistics"""
    user_data = load_user_data()
    user_id_str = str(user_id)
    
    if user_id_str in user_data:
        if check_type == "check":
            user_data[user_id_str]["cg_checks"] = user_data[user_id_str].get("cg_checks", 0) + 1
        elif check_type == "approved" and approved:
            user_data[user_id_str]["cg_approved"] = user_data[user_id_str].get("cg_approved", 0) + 1
        save_user_data(user_data)

def update_slt_stats(user_id, check_type="check", approved=False):
    """Update SLT checker statistics"""
    user_data = load_user_data()
    user_id_str = str(user_id)
    
    if user_id_str in user_data:
        if check_type == "check":
            user_data[user_id_str]["slt_checks"] = user_data[user_id_str].get("slt_checks", 0) + 1
        elif check_type == "approved" and approved:
            user_data[user_id_str]["slt_approved"] = user_data[user_id_str].get("slt_approved", 0) + 1
        save_user_data(user_data)

def update_carnage_stats(user_id, check_type="check", approved=False):
    """Update Carnage checker statistics"""
    user_data = load_user_data()
    user_id_str = str(user_id)
    
    if user_id_str in user_data:
        if check_type == "check":
            user_data[user_id_str]["carnage_checks"] = user_data[user_id_str].get("carnage_checks", 0) + 1
        elif check_type == "approved" and approved:
            user_data[user_id_str]["carnage_approved"] = user_data[user_id_str].get("carnage_approved", 0) + 1
        save_user_data(user_data)