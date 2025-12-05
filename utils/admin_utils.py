import json
import os
from config import ADMINS_FILE, ADMIN_IDS

def load_admins():
    """Load admin list from file"""
    try:
        if os.path.exists(ADMINS_FILE):
            with open(ADMINS_FILE, 'r') as f:
                data = json.load(f)
                if ADMIN_IDS[0] not in data:
                    data.append(ADMIN_IDS[0])
                return data
    except Exception as e:
        from config import logger
        logger.error(f"Error loading admins: {e}")
    return ADMIN_IDS.copy()

def save_admins(admins_list):
    """Save admin list to file"""
    try:
        with open(ADMINS_FILE, 'w') as f:
            json.dump(admins_list, f, indent=2)
    except Exception as e:
        from config import logger
        logger.error(f"Error saving admins: {e}")

def is_admin(user_id):
    """Check if user is admin"""
    admins = load_admins()
    return user_id in admins

def promote_user(user_id):
    """Promote user to admin"""
    admins = load_admins()
    if user_id not in admins:
        admins.append(user_id)
        save_admins(admins)
        return True
    return False

def demote_user(user_id):
    """Demote user from admin"""
    admins = load_admins()
    if user_id in admins and user_id != ADMIN_IDS[0]:
        admins.remove(user_id)
        save_admins(admins)
        return True
    return False

def get_admin_list():
    """Get list of all admins"""
    return load_admins()