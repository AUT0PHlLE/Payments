# Telegram Bot Payment System

A professional Telegram bot payment system with multiple subscription models, payment verification, and admin management.

## Features

- Multiple subscription plans (Monthly, 3 Months, 6 Months, 9 Months, Annual)
- Multiple payment methods support (UPI, Crypto, Stars)
- Automatic payment handle rotation (300 transactions per day limit)
- Admin verification system
- Payment verification queue
- Subscription management
- Owner-exclusive commands
- Admin management panel
- User access control

## Commands

### User Commands
- `/start` - Start the bot and check subscription status
- `/subscribe` - View subscription plans
- `/status` - Check current subscription status
- `/support` - Contact support

### Admin Commands
- `/verify <user_id>` - Verify user's payment
- `/reject <user_id>` - Reject user's payment
- `/ban <user_id>` - Ban user from the bot
- `/unban <user_id>` - Unban user
- `/stats` - View bot statistics

### Owner Commands
- `/addadmin <user_id>` - Add new admin
- `/deladmin <user_id>` - Remove admin
- `/broadcast` - Send message to all users
- `/handles` - Manage payment handles
- `/config` - Configure bot settings

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Configure the bot:
- Rename `config.example.py` to `config.py`
- Add your bot token and other configurations
- Set up your payment handles in the config

3. Run the bot:
```bash
python main.py
```

## Directory Structure
```
├── main.py
├── payment.py
├── handlers/
│   ├── __init__.py
│   ├── admin.py
│   ├── owner.py
│   ├── payment.py
│   └── user.py
├── utils/
│   ├── __init__.py
│   ├── database.py
│   └── payment_verification.py
└── config.py
```
