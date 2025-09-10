from typing import Dict, List

# Bot Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"
OWNER_ID = 123456789  # Replace with your Telegram ID
ADMIN_IDS = [123456789, 987654321]  # Replace with admin IDs

# Payment Configuration
SUBSCRIPTION_PLANS = {
    "monthly": {
        "name": "Monthly Plan",
        "price": 499,
        "duration_days": 30,
        "description": "Access bot features for 1 month"
    },
    "quarterly": {
        "name": "Quarterly Plan",
        "price": 1299,
        "duration_days": 90,
        "description": "Access bot features for 3 months"
    },
    "semi_annual": {
        "name": "Semi-Annual Plan",
        "price": 2499,
        "duration_days": 180,
        "description": "Access bot features for 6 months"
    },
    "annual": {
        "name": "Annual Plan",
        "price": 4499,
        "duration_days": 365,
        "description": "Access bot features for 12 months"
    }
}

# Payment Methods
PAYMENT_METHODS = {
    "upi": {
        "handles": [
            {"id": "upi1", "address": "merchant1@upi", "daily_limit": 300},
            {"id": "upi2", "address": "merchant2@upi", "daily_limit": 300},
            {"id": "upi3", "address": "merchant3@upi", "daily_limit": 300}
        ]
    },
    "crypto": {
        "handles": [
            {"id": "btc1", "address": "btc_address_1", "daily_limit": 100},
            {"id": "btc2", "address": "btc_address_2", "daily_limit": 100}
        ]
    }
}

# Admin Group for Payment Notifications
ADMIN_GROUP_ID = -1001234567890  # Replace with your admin group ID

# Database Configuration
DATABASE_URL = "sqlite:///bot.db"  # Replace with your database URL

# Message Templates
WELCOME_MESSAGE = """
🎉 Welcome to our Premium Bot!
To access the features, please purchase a subscription.

Available Commands:
/start - Show this message
/plans - View subscription plans
/subscribe - Start subscription process
/status - Check subscription status
"""

ADMIN_HELP = """
👑 Admin Commands:
/confirm_payment <user_id> - Confirm user payment
/reject_payment <user_id> - Reject user payment
/ban_user <user_id> - Ban user
/unban_user <user_id> - Unban user
/check_user <user_id> - Check user status
"""

OWNER_HELP = """
👑 Owner Commands:
/broadcast - Send message to all users
/stats - View bot statistics
/add_admin - Add new admin
/remove_admin - Remove admin
/update_handles - Update payment handles
"""