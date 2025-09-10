from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import random
from database import Session, User, Payment, PaymentHandle
from config import SUBSCRIPTION_PLANS, PAYMENT_METHODS, ADMIN_GROUP_ID

async def start_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{plan['name']} - ₹{plan['price']}",
                callback_data=f"plan_{plan_id}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📦 Choose your subscription plan:",
        reply_markup=reply_markup
    )

async def select_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    plan_id = query.data.split('_')[1]
    context.user_data['selected_plan'] = plan_id
    
    keyboard = []
    for method in PAYMENT_METHODS.keys():
        keyboard.append([
            InlineKeyboardButton(
                method.upper(),
                callback_data=f"payment_method_{method}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"💳 Select payment method for {SUBSCRIPTION_PLANS[plan_id]['name']}:",
        reply_markup=reply_markup
    )

async def get_payment_handle(payment_method: str) -> dict:
    session = Session()
    try:
        handles = session.query(PaymentHandle).filter_by(
            payment_method=payment_method,
            is_active=True
        ).all()
        
        available_handles = [
            h for h in handles 
            if h.daily_usage < h.daily_limit
        ]
        
        if not available_handles:
            # Reset daily usage if all handles are maxed out
            for handle in handles:
                handle.daily_usage = 0
                handle.last_reset = datetime.utcnow()
            session.commit()
            available_handles = handles
        
        selected_handle = random.choice(available_handles)
        selected_handle.daily_usage += 1
        session.commit()
        
        return {
            "handle_id": selected_handle.handle_id,
            "address": selected_handle.address
        }
    finally:
        session.close()

async def show_payment_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    payment_method = query.data.split('_')[2]
    plan_id = context.user_data['selected_plan']
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    handle = await get_payment_handle(payment_method)
    
    # Store payment info in database
    session = Session()
    try:
        payment = Payment(
            user_id=update.effective_user.id,
            amount=plan['price'],
            payment_method=payment_method,
            handle_id=handle['handle_id'],
            status='pending'
        )
        session.add(payment)
        session.commit()
        payment_id = payment.id
    finally:
        session.close()
    
    keyboard = [[
        InlineKeyboardButton(
            "✅ I've Made the Payment",
            callback_data=f"confirm_payment_{payment_id}"
        )
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
🧾 Payment Details:
Plan: {plan['name']}
Amount: ₹{plan['price']}
Method: {payment_method.upper()}
Address: {handle['address']}

Please make the payment and click the button below to submit proof.
Save your transaction ID/UTR for verification.
    """
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def submit_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    payment_id = int(query.data.split('_')[2])
    
    await query.edit_message_text(
        "📸 Please send a screenshot of your payment and the transaction ID/UTR in this format:\n\n"
        "UTR: YOUR_UTR_NUMBER\n"
        "(Attach screenshot in next message)"
    )
    
    context.user_data['awaiting_proof'] = payment_id

async def process_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'awaiting_proof' not in context.user_data:
        return
    
    payment_id = context.user_data['awaiting_proof']
    user_id = update.effective_user.id
    
    if update.message.text and update.message.text.startswith("UTR:"):
        # Save UTR
        session = Session()
        try:
            payment = session.query(Payment).get(payment_id)
            if payment:
                payment.transaction_id = update.message.text.replace("UTR:", "").strip()
                session.commit()
        finally:
            session.close()
        
        await update.message.reply_text("✅ UTR received. Please send the payment screenshot now.")
    
    elif update.message.photo:
        # Save screenshot and notify admins
        session = Session()
        try:
            payment = session.query(Payment).get(payment_id)
            if payment:
                payment.screenshot_file_id = update.message.photo[-1].file_id
                session.commit()
                
                # Notify admin group
                keyboard = [[
                    InlineKeyboardButton(
                        "✅ Approve",
                        callback_data=f"admin_approve_{payment_id}"
                    ),
                    InlineKeyboardButton(
                        "❌ Reject",
                        callback_data=f"admin_reject_{payment_id}"
                    )
                ]]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    ADMIN_GROUP_ID,
                    f"💰 New Payment Submission\n\n"
                    f"User ID: {user_id}\n"
                    f"Amount: ₹{payment.amount}\n"
                    f"Method: {payment.payment_method}\n"
                    f"UTR: {payment.transaction_id}"
                )
                
                await context.bot.send_photo(
                    ADMIN_GROUP_ID,
                    payment.screenshot_file_id,
                    reply_markup=reply_markup
                )
                
                del context.user_data['awaiting_proof']
                await update.message.reply_text(
                    "✅ Payment proof submitted successfully!\n"
                    "Please wait for admin verification."
                )
        finally:
            session.close()