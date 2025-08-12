from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import get_user
from src.utils.formatting import format_money
from src.wallet.nowpayments import create_deposit_payment, create_deposit_invoice, SUPPORTED_CRYPTOS
from src.utils.logger import logger
import asyncio
import time

def format_crypto_address(address, crypto_currency):
    """Format cryptocurrency address for better display"""
    if not address:
        return "Address not available"
    
    # For long addresses, show first 8 and last 8 characters with ... in between
    if len(address) > 20:
        return f"{address[:8]}...{address[-8:]}"
    return address

def get_network_info(crypto_currency):
    """Get network information for cryptocurrency"""
    network_info = {
        "BTC": {"network": "Bitcoin", "confirmations": "1-3", "explorer": "bitcoin"},
        "ETH": {"network": "Ethereum (ERC-20)", "confirmations": "12-35", "explorer": "ethereum"},
        "USDT": {"network": "Ethereum (ERC-20)", "confirmations": "12-35", "explorer": "ethereum"},
        "USDC": {"network": "Ethereum (ERC-20)", "confirmations": "12-35", "explorer": "ethereum"},
        "LTC": {"network": "Litecoin", "confirmations": "6-12", "explorer": "litecoin"},
        "SOL": {"network": "Solana", "confirmations": "1-2", "explorer": "solana"},
        "BNB": {"network": "BNB Smart Chain", "confirmations": "15-30", "explorer": "bnb"},
        "TRX": {"network": "Tron (TRC-20)", "confirmations": "20-30", "explorer": "tron"},
        "XMR": {"network": "Monero", "confirmations": "10-20", "explorer": "monero"},
        "DAI": {"network": "Ethereum (ERC-20)", "confirmations": "12-35", "explorer": "ethereum"},
        "DOGE": {"network": "Dogecoin", "confirmations": "6-12", "explorer": "dogecoin"},
        "SHIB": {"network": "Ethereum (ERC-20)", "confirmations": "12-35", "explorer": "ethereum"},
        "BCH": {"network": "Bitcoin Cash", "confirmations": "6-12", "explorer": "bitcoin-cash"},
        "MATIC": {"network": "Polygon", "confirmations": "128-256", "explorer": "polygon"},
        "TON": {"network": "TON", "confirmations": "1-2", "explorer": "ton"},
        "NOT": {"network": "TON", "confirmations": "1-2", "explorer": "ton"}
    }
    return network_info.get(crypto_currency, {"network": crypto_currency, "confirmations": "Variable", "explorer": "bitcoin"})

def generate_payment_uri(crypto_currency, address, amount):
    """Generate payment URI for wallet apps"""
    crypto_lower = crypto_currency.lower()
    
    # Standard cryptocurrency URI schemes
    uri_schemes = {
        "BTC": f"bitcoin:{address}?amount={amount}",
        "ETH": f"ethereum:{address}?value={amount}",
        "LTC": f"litecoin:{address}?amount={amount}",
        "BCH": f"bitcoincash:{address}?amount={amount}",
        "DOGE": f"dogecoin:{address}?amount={amount}",
        "SOL": f"solana:{address}?amount={amount}",
        "TRX": f"tron:{address}?amount={amount}"
    }
    
    return uri_schemes.get(crypto_currency, f"{crypto_lower}:{address}?amount={amount}")

async def deposit_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the deposit menu"""
    await show_deposit_menu(update, context)

async def show_deposit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the deposit amount selection menu"""
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    user = await get_user(user_id)
    
    message = (
        f"💰 **Deposit Funds** 💰\n\n"
        f"💳 Current balance: {format_money(user['balance'])}\n\n"
        f"Select deposit amount:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("💰 $10", callback_data="deposit_amount_10"),
            InlineKeyboardButton("💰 $25", callback_data="deposit_amount_25")
        ],
        [
            InlineKeyboardButton("💰 $50", callback_data="deposit_amount_50"),
            InlineKeyboardButton("💰 $100", callback_data="deposit_amount_100")
        ],
        [
            InlineKeyboardButton("💰 $250", callback_data="deposit_amount_250"),
            InlineKeyboardButton("💰 $500", callback_data="deposit_amount_500")
        ],
        [
            InlineKeyboardButton("💰 $1000", callback_data="deposit_amount_1000"),
            InlineKeyboardButton("💰 Custom", callback_data="deposit_amount_custom")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_main")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_currency_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
    """Show cryptocurrency selection menu matching Image 1 (without Card/PayPal option)"""
    message = (
        f"💰 **Select top-up currency** 💰\n\n"
        f"💵 Amount: ${amount:.2f}\n\n"
        f"Choose your preferred cryptocurrency:"
    )
    
    # Create the cryptocurrency selection keyboard matching Image 1 (without Card/PayPal)
    # Using consistent callback pattern: deposit_[crypto]_[amount]
    keyboard = [
        [
            InlineKeyboardButton("₿ Bitcoin", callback_data=f"deposit_btc_{amount}"),
            InlineKeyboardButton("⟠ Ethereum", callback_data=f"deposit_eth_{amount}")
        ],
        [
            InlineKeyboardButton("💰 USDT", callback_data=f"deposit_usdt_{amount}"),
            InlineKeyboardButton("💰 USDC", callback_data=f"deposit_usdc_{amount}")
        ],
        [
            InlineKeyboardButton("🪙 Litecoin", callback_data=f"deposit_ltc_{amount}"),
            InlineKeyboardButton("🟣 Solana", callback_data=f"deposit_sol_{amount}")
        ],
        [
            InlineKeyboardButton("🟡 BNB", callback_data=f"deposit_bnb_{amount}"),
            InlineKeyboardButton("🔴 Tron", callback_data=f"deposit_trx_{amount}")
        ],
        [
            InlineKeyboardButton("🔒 Monero", callback_data=f"deposit_xmr_{amount}"),
            InlineKeyboardButton("🟠 DAI", callback_data=f"deposit_dai_{amount}")
        ],
        [
            InlineKeyboardButton("🐕 Dogecoin", callback_data=f"deposit_doge_{amount}"),
            InlineKeyboardButton("🐕 Shiba Inu", callback_data=f"deposit_shib_{amount}")
        ],
        [
            InlineKeyboardButton("₿ Bitcoin Cash", callback_data=f"deposit_bch_{amount}"),
            InlineKeyboardButton("🟣 Polygon", callback_data=f"deposit_matic_{amount}")
        ],
        [
            InlineKeyboardButton("💎 Toncoin", callback_data=f"deposit_ton_{amount}"),
            InlineKeyboardButton("🪙 NotCoin", callback_data=f"deposit_not_{amount}")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def deposit_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit menu callback queries with comprehensive error handling"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    logger.info(f"Deposit callback received from user {user_id}: {callback_data}")
    
    try:
        await query.answer()
        
        data = callback_data.split("_")
        
        if len(data) < 2:
            logger.warning(f"Invalid callback data format: {callback_data}")
            await query.edit_message_text("❌ Invalid request. Please try again.")
            return
        
        action = data[1]
        logger.debug(f"Processing deposit action: {action} for user {user_id}")
        
        if action == "amount":
            # Handle deposit amount selection
            if len(data) >= 3:
                if data[2] == "custom":
                    logger.info(f"User {user_id} selected custom deposit amount")
                    # Store in context that we're waiting for a custom amount
                    context.user_data["deposit_action"] = "custom_amount"
                    context.user_data["deposit_timestamp"] = time.time()
                    
                    message = (
                        "💰 **Custom Deposit Amount** 💰\n\n"
                        "Please enter the amount you want to deposit:\n"
                        "💵 Minimum: $10\n"
                        "💵 Maximum: $10,000\n\n"
                        "Example: 25.50\n\n"
                        "⏰ This request will expire in 5 minutes."
                    )
                    
                    keyboard = [
                        [
                            InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                else:
                    try:
                        amount = float(data[2])
                        logger.info(f"User {user_id} selected deposit amount: ${amount}")
                        
                        # Validate amount
                        if amount < 10:
                            logger.warning(f"User {user_id} tried to deposit below minimum: ${amount}")
                            await query.edit_message_text(
                                "❌ **Minimum Deposit Error**\n\n"
                                "The minimum deposit amount is $10.\n"
                                "Please select a higher amount.",
                                reply_markup=InlineKeyboardMarkup([[
                                    InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                                ]]),
                                parse_mode='Markdown'
                            )
                            return
                        
                        if amount > 10000:
                            logger.warning(f"User {user_id} tried to deposit above maximum: ${amount}")
                            await query.edit_message_text(
                                "❌ **Maximum Deposit Error**\n\n"
                                "The maximum deposit amount is $10,000.\n"
                                "Please select a lower amount or contact support for larger deposits.",
                                reply_markup=InlineKeyboardMarkup([[
                                    InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                                ]]),
                                parse_mode='Markdown'
                            )
                            return
                        
                        await show_currency_selection(update, context, amount)
                        
                    except ValueError as e:
                        logger.error(f"Invalid amount format from user {user_id}: {data[2]} - {str(e)}")
                        await query.edit_message_text(
                            "❌ **Invalid Amount Format**\n\n"
                            "Please select a valid deposit amount from the menu.",
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                            ]]),
                            parse_mode='Markdown'
                        )
            else:
                logger.warning(f"Incomplete amount callback data from user {user_id}: {callback_data}")
                await query.edit_message_text("❌ Invalid amount selection. Please try again.")
        
        elif action in SUPPORTED_CRYPTOS or action.lower() in [crypto.lower() for crypto in SUPPORTED_CRYPTOS]:
            # Handle cryptocurrency selection - improved pattern matching
            if len(data) >= 3:
                try:
                    crypto_currency = action.upper()
                    amount = float(data[2])
                    
                    logger.info(f"User {user_id} selected {crypto_currency} for ${amount} deposit")
                    
                    # Validate cryptocurrency is supported
                    if crypto_currency not in SUPPORTED_CRYPTOS:
                        logger.error(f"Unsupported cryptocurrency selected by user {user_id}: {crypto_currency}")
                        await query.edit_message_text(
                            f"❌ **Cryptocurrency Not Supported**\n\n"
                            f"{crypto_currency} is not currently supported.\n"
                            f"Please choose from our supported cryptocurrencies.",
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                            ]]),
                            parse_mode='Markdown'
                        )
                        return
                    
                    await process_crypto_deposit(update, context, crypto_currency, amount)
                    
                except ValueError as e:
                    logger.error(f"Invalid amount in crypto callback from user {user_id}: {data[2]} - {str(e)}")
                    await query.edit_message_text(
                        "❌ **Invalid Amount**\n\n"
                        "There was an error processing your deposit amount.\n"
                        "Please try again.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                        ]]),
                        parse_mode='Markdown'
                    )
            else:
                logger.warning(f"Incomplete crypto callback data from user {user_id}: {callback_data}")
                await query.edit_message_text("❌ Invalid cryptocurrency selection. Please try again.")
        
        elif action == "show" and len(data) >= 4 and data[2] == "payment":
            # Handle showing payment details again
            payment_id = data[3]
            logger.info(f"User {user_id} requested to show payment details: {payment_id}")
            await show_payment_details(update, context, payment_id)
        
        elif action == "check" and len(data) >= 4 and data[2] == "payment":
            # Handle payment status check
            payment_id = data[3]
            logger.info(f"User {user_id} requested payment status check: {payment_id}")
            await check_payment_status_callback(update, context, payment_id)
    
        elif action == "copy" and len(data) >= 4:
            # Handle copy functionality
            copy_type = data[2]  # "address" or "amount"
            payment_id = data[3]
            logger.info(f"User {user_id} requested to copy {copy_type} for payment {payment_id}")
            
            payment_info = context.user_data.get(f"payment_{payment_id}")
            
            if payment_info:
                try:
                    crypto_currency = payment_info['crypto_currency']
                    payment_address = payment_info['payment_address']
                    pay_amount = payment_info['pay_amount']
                    
                    if copy_type == "address":
                        message = (
                            f"📋 **Copy {crypto_currency} Address** 📋\n\n"
                            f"**Deposit Address:**\n"
                            f"`{payment_address}`\n\n"
                            f"📱 **How to copy:**\n"
                            f"• **Mobile:** Tap and hold the address above\n"
                            f"• **Desktop:** Select the address and Ctrl+C\n\n"
                            f"⚠️ **Important:** Make sure you copy the complete address!\n\n"
                            f"💡 **Next steps:**\n"
                            f"1. Copy this address\n"
                            f"2. Open your {crypto_currency} wallet\n"
                            f"3. Paste the address in the 'Send to' field\n"
                            f"4. Enter amount: `{pay_amount} {crypto_currency}`"
                        )
                    elif copy_type == "amount":
                        message = (
                            f"📋 **Copy {crypto_currency} Amount** 📋\n\n"
                            f"**Exact Amount to Send:**\n"
                            f"`{pay_amount}`\n\n"
                            f"📱 **How to copy:**\n"
                            f"• **Mobile:** Tap and hold the amount above\n"
                            f"• **Desktop:** Select the amount and Ctrl+C\n\n"
                            f"⚠️ **Critical:** Send EXACTLY this amount!\n"
                            f"• Too little = payment not detected\n"
                            f"• Too much = overpayment (may be lost)\n\n"
                            f"💡 **Tip:** Copy this amount and paste it in your wallet's amount field."
                        )
                    else:
                        logger.warning(f"Invalid copy type requested by user {user_id}: {copy_type}")
                        message = "❌ Invalid copy request."
                    
                    keyboard = [
                        [
                            InlineKeyboardButton("📋 Copy Address", callback_data=f"deposit_copy_address_{payment_id}"),
                            InlineKeyboardButton("📋 Copy Amount", callback_data=f"deposit_copy_amount_{payment_id}")
                        ],
                        [
                            InlineKeyboardButton("✅ Check Payment Status", callback_data=f"deposit_check_payment_{payment_id}")
                        ],
                        [
                            InlineKeyboardButton("🔙 Back to Payment", callback_data=f"deposit_show_payment_{payment_id}"),
                            InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                    
                except KeyError as e:
                    logger.error(f"Missing payment info key for user {user_id}, payment {payment_id}: {str(e)}")
                    await query.edit_message_text(
                        "❌ **Payment Information Incomplete**\n\n"
                        "Some payment details are missing. Please create a new deposit.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
                        ]]),
                        parse_mode='Markdown'
                    )
            else:
                logger.warning(f"Payment information not found for user {user_id}, payment {payment_id}")
                await query.edit_message_text(
                    "❌ **Payment Not Found**\n\n"
                    "Payment information has expired or was not found.\n"
                    "Please create a new deposit.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
                    ]]),
                    parse_mode='Markdown'
                )
        
        else:
            logger.warning(f"Unhandled deposit callback from user {user_id}: {callback_data}")
            await query.edit_message_text(
                "❌ **Unknown Request**\n\n"
                "This action is not recognized. Please try again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
                ]]),
                parse_mode='Markdown'
            )
    
    except Exception as e:
        logger.error(f"Error in deposit callback for user {user_id}: {str(e)}", exc_info=True)
        try:
            await query.edit_message_text(
                "❌ **System Error**\n\n"
                "An unexpected error occurred. Please try again later.\n"
                "If the problem persists, contact support.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
                ]]),
                parse_mode='Markdown'
            )
        except Exception as edit_error:
            logger.error(f"Failed to send error message to user {user_id}: {str(edit_error)}")

async def show_payment_details(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: str):
    """Show payment details again"""
    payment_info = context.user_data.get(f"payment_{payment_id}")
    
    if not payment_info:
        await update.callback_query.edit_message_text("❌ Payment information not found.")
        return
    
    crypto_currency = payment_info['crypto_currency']
    payment_address = payment_info['payment_address']
    pay_amount = payment_info['pay_amount']
    amount_usd = payment_info['amount_usd']
    
    # Get network information
    network_info = get_network_info(crypto_currency)
    
    message = (
        f"💰 **{crypto_currency} Deposit Payment** 💰\n\n"
        f"💵 **USD Amount:** ${amount_usd:.2f}\n"
        f"💰 **Pay Exactly:** `{pay_amount} {crypto_currency}`\n\n"
        f"📍 **Deposit Address:**\n"
        f"```\n{payment_address}\n```\n\n"
        f"🌐 **Network:** {network_info['network']}\n"
        f"⏱️ **Confirmations:** {network_info['confirmations']} blocks\n"
        f"⏰ **Expires:** 30 minutes\n\n"
        f"⚠️ **CRITICAL INSTRUCTIONS:**\n"
        f"• Send ONLY {crypto_currency} to this address\n"
        f"• Send EXACTLY `{pay_amount} {crypto_currency}`\n"
        f"• Use {network_info['network']} network\n"
        f"• Double-check the address before sending\n\n"
        f"🔍 **Payment ID:** `{payment_id}`\n\n"
        f"💡 **How to pay:**\n"
        f"1. Click 'Copy Address' below\n"
        f"2. Open your {crypto_currency} wallet\n"
        f"3. Paste the address and enter the exact amount\n"
        f"4. Send the transaction\n"
        f"5. Click 'Check Payment Status' to monitor\n\n"
        f"✅ **Auto-credit:** Funds credited after blockchain confirmation!"
    )
    
    # Generate payment URI for wallet apps
    payment_uri = generate_payment_uri(crypto_currency, payment_address, pay_amount)
    explorer_url = f"https://blockchair.com/{network_info['explorer']}/address/{payment_address}"
    
    keyboard = [
        [
            InlineKeyboardButton("📋 Copy Address", callback_data=f"deposit_copy_address_{payment_id}"),
            InlineKeyboardButton("📋 Copy Amount", callback_data=f"deposit_copy_amount_{payment_id}")
        ],
        [
            InlineKeyboardButton("📱 Open in Wallet", url=payment_uri),
            InlineKeyboardButton("🔍 View on Explorer", url=explorer_url)
        ],
        [
            InlineKeyboardButton("✅ Check Payment Status", callback_data=f"deposit_check_payment_{payment_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def check_payment_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: str):
    """Check payment status and update user with comprehensive error handling"""
    from src.wallet.nowpayments import check_payment_status
    
    user_id = update.callback_query.from_user.id
    logger.info(f"Checking payment status for user {user_id}, payment {payment_id}")
    
    try:
        # Show checking message
        await update.callback_query.edit_message_text(
            "🔄 **Checking Payment Status...**\n\n"
            "Please wait while we check your payment status...",
            parse_mode='Markdown'
        )
        
        # Add small delay to show the checking message
        await asyncio.sleep(1)
        
        payment_status = await check_payment_status(payment_id)
        
        if payment_status:
            status = payment_status.get("payment_status", "waiting")
            payment_info = context.user_data.get(f"payment_{payment_id}")
            
            logger.info(f"Payment status for user {user_id}, payment {payment_id}: {status}")
            
            # Update stored payment info with latest status
            if payment_info:
                payment_info["payment_status"] = status
                payment_info["last_checked"] = time.time()
            
            if status in ["confirmed", "finished"]:
                logger.info(f"Payment confirmed for user {user_id}, payment {payment_id}")
                
                # Clean up payment info from context since it's completed
                if f"payment_{payment_id}" in context.user_data:
                    del context.user_data[f"payment_{payment_id}"]
                
                message = (
                    "✅ **Payment Confirmed!** ✅\n\n"
                    "🎉 Your deposit has been confirmed and credited to your account!\n\n"
                    "💰 Funds are now available in your balance.\n"
                    "🎮 You can start playing games immediately!\n\n"
                    "Thank you for your deposit!"
                )
                
                keyboard = [
                    [
                        InlineKeyboardButton("🎮 Play Games", callback_data="menu_games"),
                        InlineKeyboardButton("💰 Check Balance", callback_data="menu_profile")
                    ],
                    [
                        InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")
                    ]
                ]
                
            elif status in ["waiting", "confirming", "sending"]:
                crypto_currency = payment_info.get("crypto_currency", "crypto") if payment_info else "crypto"
                pay_amount = payment_info.get("pay_amount", "amount") if payment_info else "amount"
                created_at = payment_info.get("created_at", time.time()) if payment_info else time.time()
                
                # Calculate time elapsed
                elapsed_minutes = int((time.time() - created_at) / 60)
                
                if status == "waiting":
                    status_text = "⏳ **Waiting for Payment**"
                    status_desc = f"We haven't received your {crypto_currency} payment yet."
                elif status == "confirming":
                    status_text = "🔄 **Confirming Payment**"
                    status_desc = f"Your {crypto_currency} payment is being confirmed on the blockchain."
                else:  # sending
                    status_text = "📤 **Processing Payment**"
                    status_desc = f"Your {crypto_currency} payment is being processed."
                
                message = (
                    f"{status_text}\n\n"
                    f"{status_desc}\n"
                    f"Expected amount: `{pay_amount} {crypto_currency}`\n\n"
                    f"⏰ **Time elapsed:** {elapsed_minutes} minutes\n"
                    f"⏱️ **Typical confirmation time:** 10-30 minutes\n\n"
                    f"**What to do:**\n"
                    f"• If you haven't sent the payment yet, please send it now\n"
                    f"• If you've sent it, please wait for blockchain confirmation\n"
                    f"• Network congestion may cause delays\n\n"
                    f"💡 **Tip:** Check again in 5-10 minutes"
                )
                
                keyboard = [
                    [
                        InlineKeyboardButton("🔄 Check Again", callback_data=f"deposit_check_payment_{payment_id}"),
                        InlineKeyboardButton("📋 Payment Details", callback_data=f"deposit_show_payment_{payment_id}")
                    ],
                    [
                        InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
                    ]
                ]
                
            elif status in ["expired", "failed"]:
                logger.warning(f"Payment {status} for user {user_id}, payment {payment_id}")
                
                # Clean up expired/failed payment info
                if f"payment_{payment_id}" in context.user_data:
                    del context.user_data[f"payment_{payment_id}"]
                
                if status == "expired":
                    message = (
                        "⏰ **Payment Expired** ⏰\n\n"
                        "This payment has expired (30 minutes limit).\n\n"
                        "**What happened:**\n"
                        "• Payment wasn't received within the time limit\n"
                        "• The deposit address is no longer valid\n\n"
                        "**Next steps:**\n"
                        "• Create a new deposit with a fresh address\n"
                        "• If you sent payment to the old address, contact support"
                    )
                else:  # failed
                    message = (
                        "❌ **Payment Failed** ❌\n\n"
                        "This payment has failed.\n\n"
                        "**Possible reasons:**\n"
                        "• Incorrect amount sent\n"
                        "• Wrong cryptocurrency or network\n"
                        "• Technical issue with payment processing\n\n"
                        "**Next steps:**\n"
                        "• Create a new deposit\n"
                        "• If you sent payment, contact support for assistance"
                    )
                
                keyboard = [
                    [
                        InlineKeyboardButton("💰 New Deposit", callback_data="menu_deposit")
                    ],
                    [
                        InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")
                    ]
                ]
                
            else:
                # Unknown status
                logger.warning(f"Unknown payment status for user {user_id}, payment {payment_id}: {status}")
                
                message = (
                    f"ℹ️ **Payment Status: {status.capitalize()}**\n\n"
                    "Your payment is being processed.\n\n"
                    "**Current status:** {status}\n"
                    "**What to do:**\n"
                    "• If you've sent the payment, please wait for confirmation\n"
                    "• If you haven't sent it yet, please follow the payment instructions\n"
                    "• Check again in a few minutes\n\n"
                    "For assistance, please contact support."
                )
                
                keyboard = [
                    [
                        InlineKeyboardButton("🔄 Check Again", callback_data=f"deposit_check_payment_{payment_id}"),
                        InlineKeyboardButton("📋 Payment Details", callback_data=f"deposit_show_payment_{payment_id}")
                    ],
                    [
                        InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
                    ]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
        else:
            logger.error(f"No payment status returned for user {user_id}, payment {payment_id}")
            
            message = (
                "❌ **Status Check Failed**\n\n"
                "Could not retrieve payment status from the payment service.\n\n"
                "**Possible causes:**\n"
                "• Payment service temporarily unavailable\n"
                "• Network connectivity issues\n"
                "• Payment ID not found\n\n"
                "**Solutions:**\n"
                "• Try again in a few minutes\n"
                "• Check your internet connection\n"
                "• Contact support if problem persists"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Try Again", callback_data=f"deposit_check_payment_{payment_id}")
                ],
                [
                    InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    except asyncio.TimeoutError:
        logger.error(f"Timeout checking payment status for user {user_id}, payment {payment_id}")
        await update.callback_query.edit_message_text(
            "⏰ **Status Check Timeout**\n\n"
            "The status check took too long to complete.\n"
            "This usually happens during high network traffic.\n\n"
            "Please try again in a moment.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 Try Again", callback_data=f"deposit_check_payment_{payment_id}"),
                    InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                ]
            ]),
            parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f"Error checking payment status for user {user_id}, payment {payment_id}: {str(e)}", exc_info=True)
        
        # Determine error type for better user messaging
        error_message = "An unexpected error occurred while checking payment status."
        if "network" in str(e).lower() or "connection" in str(e).lower():
            error_message = "Network connection error. Please check your internet connection."
        elif "timeout" in str(e).lower():
            error_message = "Request timed out. Please try again."
        elif "api" in str(e).lower():
            error_message = "Payment service error. Please try again later."
        
        await update.callback_query.edit_message_text(
            f"❌ **Status Check Error**\n\n"
            f"**Error:** {error_message}\n\n"
            f"**Technical details:** {str(e)[:100]}...\n\n"
            f"Please try again later or contact support if the problem persists.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 Try Again", callback_data=f"deposit_check_payment_{payment_id}"),
                    InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                ]
            ]),
            parse_mode='Markdown'
        )

async def process_crypto_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE, crypto_currency: str, amount: float):
    """Process cryptocurrency deposit with comprehensive error handling"""
    user_id = update.callback_query.from_user.id
    
    logger.info(f"Processing {crypto_currency} deposit for user {user_id}: ${amount}")
    
    # Check for rate limiting - prevent spam
    last_deposit_time = context.user_data.get("last_deposit_attempt", 0)
    current_time = time.time()
    if current_time - last_deposit_time < 10:  # 10 second cooldown
        logger.warning(f"Rate limit hit for user {user_id}")
        await update.callback_query.edit_message_text(
            "⏰ **Please Wait**\n\n"
            "You're creating deposits too quickly.\n"
            "Please wait a moment before trying again.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
            ]]),
            parse_mode='Markdown'
        )
        return
    
    context.user_data["last_deposit_attempt"] = current_time
    
    try:
        # Show processing message
        await update.callback_query.edit_message_text(
            f"⏳ **Creating {crypto_currency} Payment...**\n\n"
            f"💵 Amount: ${amount:.2f}\n"
            f"💰 Currency: {crypto_currency}\n\n"
            f"Please wait while we generate your payment address...",
            parse_mode='Markdown'
        )
        
        # Validate cryptocurrency is supported
        if crypto_currency not in SUPPORTED_CRYPTOS:
            logger.error(f"Unsupported cryptocurrency requested by user {user_id}: {crypto_currency}")
            await update.callback_query.edit_message_text(
                f"❌ **Cryptocurrency Not Supported**\n\n"
                f"{crypto_currency} is not currently supported.\n\n"
                f"**Supported cryptocurrencies:**\n"
                f"{', '.join(SUPPORTED_CRYPTOS[:10])}\n"
                f"...and {len(SUPPORTED_CRYPTOS)-10} more",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                ]]),
                parse_mode='Markdown'
            )
            return
        
        # Check if NOWPayments API is available
        from src.wallet.nowpayments import get_api_status
        api_status = await get_api_status()
        if not api_status or api_status.get("message") != "OK":
            logger.error(f"NOWPayments API unavailable for user {user_id}: {api_status}")
            await update.callback_query.edit_message_text(
                "❌ **Payment Service Unavailable**\n\n"
                "Our payment service is temporarily unavailable.\n"
                "Please try again in a few minutes.\n\n"
                "If the problem persists, contact support.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Try Again", callback_data=f"deposit_{crypto_currency.lower()}_{amount}"),
                    InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                ]]),
                parse_mode='Markdown'
            )
            return
        
        # Create payment using NOWPayments
        logger.debug(f"Creating NOWPayments payment for user {user_id}")
        payment = await create_deposit_payment(user_id, amount, crypto_currency)
        
        if payment and payment.get("payment_id"):
            payment_id = payment.get("payment_id")
            payment_address = payment.get("pay_address")
            pay_amount = payment.get("pay_amount")
            
            # Validate payment response
            if not payment_address or not pay_amount:
                logger.error(f"Incomplete payment response for user {user_id}: {payment}")
                await update.callback_query.edit_message_text(
                    "❌ **Payment Creation Failed**\n\n"
                    "The payment was created but some details are missing.\n"
                    "Please try again or contact support.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔄 Try Again", callback_data=f"deposit_{crypto_currency.lower()}_{amount}"),
                        InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                    ]]),
                    parse_mode='Markdown'
                )
                return
            
            logger.info(f"Payment created successfully for user {user_id}: {payment_id}")
            
            # Store payment info in context for tracking
            context.user_data[f"payment_{payment_id}"] = {
                "user_id": user_id,
                "amount_usd": amount,
                "crypto_currency": crypto_currency,
                "payment_address": payment_address,
                "pay_amount": pay_amount,
                "created_at": current_time,
                "payment_status": "waiting"
            }
            
            # Get network information
            network_info = get_network_info(crypto_currency)
            
            message = (
                f"💰 **{crypto_currency} Deposit Payment** 💰\n\n"
                f"💵 **USD Amount:** ${amount:.2f}\n"
                f"💰 **Pay Exactly:** `{pay_amount} {crypto_currency}`\n\n"
                f"📍 **Deposit Address:**\n"
                f"```\n{payment_address}\n```\n\n"
                f"🌐 **Network:** {network_info['network']}\n"
                f"⏱️ **Confirmations:** {network_info['confirmations']} blocks\n"
                f"⏰ **Expires:** 30 minutes\n\n"
                f"⚠️ **CRITICAL INSTRUCTIONS:**\n"
                f"• Send ONLY {crypto_currency} to this address\n"
                f"• Send EXACTLY `{pay_amount} {crypto_currency}`\n"
                f"• Use {network_info['network']} network\n"
                f"• Double-check the address before sending\n\n"
                f"🔍 **Payment ID:** `{payment_id}`\n\n"
                f"💡 **How to pay:**\n"
                f"1. Click 'Copy Address' below\n"
                f"2. Open your {crypto_currency} wallet\n"
                f"3. Paste the address and enter the exact amount\n"
                f"4. Send the transaction\n"
                f"5. Click 'Check Payment Status' to monitor\n\n"
                f"✅ **Auto-credit:** Funds credited after blockchain confirmation!"
            )
            
            # Generate payment URI for wallet apps
            payment_uri = generate_payment_uri(crypto_currency, payment_address, pay_amount)
            explorer_url = f"https://blockchair.com/{network_info['explorer']}/address/{payment_address}"
            
            keyboard = [
                [
                    InlineKeyboardButton("📋 Copy Address", callback_data=f"deposit_copy_address_{payment_id}"),
                    InlineKeyboardButton("📋 Copy Amount", callback_data=f"deposit_copy_amount_{payment_id}")
                ],
                [
                    InlineKeyboardButton("📱 Open in Wallet", url=payment_uri),
                    InlineKeyboardButton("🔍 View on Explorer", url=explorer_url)
                ],
                [
                    InlineKeyboardButton("✅ Check Payment Status", callback_data=f"deposit_check_payment_{payment_id}")
                ],
                [
                    InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
        else:
            # Handle payment creation failure
            error_details = "Unknown error"
            if payment:
                if "message" in payment:
                    error_details = payment["message"]
                elif "error" in payment:
                    error_details = payment["error"]
                logger.error(f"Payment creation failed for user {user_id}: {payment}")
            else:
                logger.error(f"Payment creation returned None for user {user_id}")
            
            await update.callback_query.edit_message_text(
                "❌ **Payment Creation Failed**\n\n"
                f"**Error:** {error_details}\n\n"
                "**Possible causes:**\n"
                "• Payment service temporarily unavailable\n"
                "• Network connectivity issues\n"
                "• Invalid amount or currency\n\n"
                "**Solutions:**\n"
                "• Try again in a few minutes\n"
                "• Try a different cryptocurrency\n"
                "• Contact support if problem persists",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🔄 Try Again", callback_data=f"deposit_{crypto_currency.lower()}_{amount}"),
                        InlineKeyboardButton("💱 Different Crypto", callback_data=f"deposit_amount_{amount}")
                    ],
                    [
                        InlineKeyboardButton("🔙 Back to Deposit", callback_data="menu_deposit")
                    ]
                ]),
                parse_mode='Markdown'
            )
    
    except asyncio.TimeoutError:
        logger.error(f"Timeout creating payment for user {user_id}")
        await update.callback_query.edit_message_text(
            "⏰ **Request Timeout**\n\n"
            "The payment creation took too long.\n"
            "This usually happens during high network traffic.\n\n"
            "Please try again in a moment.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 Try Again", callback_data=f"deposit_{crypto_currency.lower()}_{amount}"),
                    InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                ]
            ]),
            parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f"Unexpected error processing deposit for user {user_id}: {str(e)}", exc_info=True)
        
        # Determine error type for better user messaging
        error_message = "An unexpected error occurred."
        if "network" in str(e).lower() or "connection" in str(e).lower():
            error_message = "Network connection error. Please check your internet connection."
        elif "timeout" in str(e).lower():
            error_message = "Request timed out. Please try again."
        elif "api" in str(e).lower():
            error_message = "Payment service error. Please try again later."
        
        await update.callback_query.edit_message_text(
            f"❌ **System Error**\n\n"
            f"**Error:** {error_message}\n\n"
            f"**Technical details:** {str(e)[:100]}...\n\n"
            f"Please try again later or contact support if the problem persists.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 Try Again", callback_data=f"deposit_{crypto_currency.lower()}_{amount}"),
                    InlineKeyboardButton("🔙 Back", callback_data="menu_deposit")
                ]
            ]),
            parse_mode='Markdown'
        )

async def deposit_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit-related messages with improved validation"""
    user_id = update.effective_user.id
    
    if "deposit_action" not in context.user_data:
        return False
    
    action = context.user_data["deposit_action"]
    
    if action == "custom_amount":
        logger.info(f"Processing custom amount from user {user_id}: {update.message.text}")
        
        # Check if request has expired (5 minutes)
        request_time = context.user_data.get("deposit_timestamp", 0)
        if time.time() - request_time > 300:  # 5 minutes
            logger.warning(f"Custom amount request expired for user {user_id}")
            del context.user_data["deposit_action"]
            if "deposit_timestamp" in context.user_data:
                del context.user_data["deposit_timestamp"]
            
            await update.message.reply_text(
                "⏰ **Request Expired**\n\n"
                "Your custom amount request has expired.\n"
                "Please start a new deposit to continue.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💰 New Deposit", callback_data="menu_deposit")
                ]]),
                parse_mode='Markdown'
            )
            return True
        
        # Process custom deposit amount
        try:
            user_input = update.message.text.strip()
            
            # Remove common currency symbols and text
            cleaned_input = user_input.replace('$', '').replace('USD', '').replace('usd', '').strip()
            
            amount = float(cleaned_input)
            
            logger.debug(f"Parsed amount from user {user_id}: ${amount}")
            
            if amount < 10:
                logger.warning(f"User {user_id} entered amount below minimum: ${amount}")
                await update.message.reply_text(
                    "❌ **Amount Too Low**\n\n"
                    f"You entered: ${amount:.2f}\n"
                    f"Minimum deposit: $10.00\n\n"
                    f"Please enter an amount of $10 or more.",
                    parse_mode='Markdown'
                )
                return True
            
            if amount > 10000:
                logger.warning(f"User {user_id} entered amount above maximum: ${amount}")
                await update.message.reply_text(
                    "❌ **Amount Too High**\n\n"
                    f"You entered: ${amount:.2f}\n"
                    f"Maximum deposit: $10,000.00\n\n"
                    f"Please enter an amount of $10,000 or less.\n"
                    f"For larger deposits, contact support.",
                    parse_mode='Markdown'
                )
                return True
            
            # Validate reasonable decimal places
            if len(str(amount).split('.')[-1]) > 2:
                amount = round(amount, 2)
                logger.debug(f"Rounded amount for user {user_id}: ${amount}")
            
            # Clear the deposit action
            del context.user_data["deposit_action"]
            if "deposit_timestamp" in context.user_data:
                del context.user_data["deposit_timestamp"]
            
            logger.info(f"Valid custom amount from user {user_id}: ${amount}")
            
            # Show currency selection for this amount
            # We need to create a fake callback query to use the existing function
            class FakeQuery:
                def __init__(self, user_id):
                    self.from_user = type('obj', (object,), {'id': user_id})
                    
                async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
                    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            
            fake_update = type('obj', (object,), {'callback_query': FakeQuery(user_id)})
            await show_currency_selection(fake_update, context, amount)
            
        except ValueError as e:
            logger.warning(f"Invalid amount format from user {user_id}: {update.message.text} - {str(e)}")
            await update.message.reply_text(
                "❌ **Invalid Amount Format**\n\n"
                f"You entered: `{update.message.text}`\n\n"
                f"**Valid formats:**\n"
                f"• `25` (whole number)\n"
                f"• `25.50` (with decimals)\n"
                f"• `$25.50` (with dollar sign)\n\n"
                f"Please enter a valid number between $10 and $10,000.",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Unexpected error processing custom amount for user {user_id}: {str(e)}")
            await update.message.reply_text(
                "❌ **Processing Error**\n\n"
                "There was an error processing your amount.\n"
                "Please try again or select a preset amount.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💰 Preset Amounts", callback_data="menu_deposit")
                ]]),
                parse_mode='Markdown'
            )
        
        return True
    
    return False