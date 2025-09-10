from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN, WELCOME_MESSAGE
from database import init_db
import payment
import admin_commands
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context):
    """Send welcome message when /start is issued."""
    await update.message.reply_text(WELCOME_MESSAGE)

async def check_subscription(update: Update, context) -> bool:
    """Check if user has active subscription"""
    user_id = update.effective_user.id
    session = Session()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return False
        if user.banned:
            await update.message.reply_text("⛔️ You are banned from using this bot.")
            return False
        if not user.is_premium or (user.subscription_end and user.subscription_end < datetime.utcnow()):
            await update.message.reply_text(
                "⚠️ You need an active subscription to use this feature.\n"
                "Use /subscribe to purchase a subscription."
            )
            return False
        return True
    finally:
        session.close()

def main():
    """Start the bot."""
    # Initialize database
    init_db()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", payment.start_subscription))
    
    # Payment handlers
    application.add_handler(CallbackQueryHandler(
        payment.select_payment_method,
        pattern="^plan_"
    ))
    application.add_handler(CallbackQueryHandler(
        payment.show_payment_details,
        pattern="^payment_method_"
    ))
    application.add_handler(CallbackQueryHandler(
        payment.submit_payment_proof,
        pattern="^confirm_payment_"
    ))
    application.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO,
        payment.process_payment_proof
    ))
    
    # Admin handlers
    application.add_handler(CallbackQueryHandler(
        admin_commands.admin_approve_payment,
        pattern="^admin_approve_"
    ))
    application.add_handler(CallbackQueryHandler(
        admin_commands.admin_reject_payment,
        pattern="^admin_reject_"
    ))
    application.add_handler(CommandHandler(
        "broadcast",
        admin_commands.broadcast_message
    ))
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()