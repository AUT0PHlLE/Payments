from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database import Session, User, Payment
from config import OWNER_ID, ADMIN_IDS

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

async def admin_approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin_id = update.effective_user.id
    
    if not is_admin(admin_id):
        await query.answer("⛔️ You are not authorized!")
        return
    
    payment_id = int(query.data.split('_')[2])
    
    session = Session()
    try:
        payment = session.query(Payment).get(payment_id)
        if payment and payment.status == 'pending':
            payment.status = 'confirmed'
            payment.confirmed_at = datetime.utcnow()
            payment.confirmed_by = admin_id
            
            # Update user subscription
            user = session.query(User).filter_by(user_id=payment.user_id).first()
            if user:
                user.is_premium = True
                if user.subscription_end and user.subscription_end > datetime.utcnow():
                    user.subscription_end += timedelta(days=30)
                else:
                    user.subscription_end = datetime.utcnow() + timedelta(days=30)
            
            session.commit()
            
            # Notify user
            await context.bot.send_message(
                payment.user_id,
                "🎉 Your payment has been confirmed!\n"
                "You now have access to all bot features."
            )
            
            await query.edit_message_text(
                f"✅ Payment #{payment_id} approved by admin {admin_id}"
            )
    finally:
        session.close()

async def admin_reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin_id = update.effective_user.id
    
    if not is_admin(admin_id):
        await query.answer("⛔️ You are not authorized!")
        return
    
    payment_id = int(query.data.split('_')[2])
    
    session = Session()
    try:
        payment = session.query(Payment).get(payment_id)
        if payment and payment.status == 'pending':
            payment.status = 'rejected'
            payment.confirmed_at = datetime.utcnow()
            payment.confirmed_by = admin_id
            session.commit()
            
            # Notify user
            await context.bot.send_message(
                payment.user_id,
                "❌ Your payment was rejected.\n"
                "Please contact support for assistance."
            )
            
            await query.edit_message_text(
                f"❌ Payment #{payment_id} rejected by admin {admin_id}"
            )
    finally:
        session.close()

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("⛔️ This command is only for the owner!")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a message to broadcast!")
        return
    
    message = " ".join(context.args)
    
    session = Session()
    try:
        users = session.query(User).all()
        success = 0
        failed = 0
        
        for user in users:
            try:
                await context.bot.send_message(user.user_id, message)
                success += 1
            except:
                failed += 1
        
        await update.message.reply_text(
            f"📢 Broadcast completed!\n"
            f"✅ Success: {success}\n"
            f"❌ Failed: {failed}"
        )
    finally:
        session.close()