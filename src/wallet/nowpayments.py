import os
import json
import aiohttp
import logging
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# NOWPayments API configuration
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")
NOWPAYMENTS_BASE_URL = "https://api.nowpayments.io/v1"
NOWPAYMENTS_IPN_SECRET = os.getenv("NOWPAYMENTS_IPN_SECRET", "")  # For IPN verification

if not NOWPAYMENTS_API_KEY:
    logger.warning("NOWPAYMENTS_API_KEY not set - crypto payments will not work")

# Supported cryptocurrencies for our bot (based on NOWPayments API)
SUPPORTED_CRYPTOS = [
    "BTC", "ETH", "USDT", "USDC", "LTC", "SOL", "BNB", "TRX", 
    "XMR", "DAI", "DOGE", "SHIB", "BCH", "MATIC", "TON", "NOT",
    "XRP", "ADA", "DOT", "AVAX"  # Additional supported cryptos
]

class NOWPaymentsAPI:
    """Class to handle NOWPayments API interactions"""
    
    def __init__(self, api_key=NOWPAYMENTS_API_KEY):
        self.api_key = api_key
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def get_status(self):
        """Get API status"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{NOWPAYMENTS_BASE_URL}/status",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Failed to get API status: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting API status: {str(e)}")
            return None
    
    async def get_available_currencies(self):
        """Get list of available currencies from NOWPayments"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{NOWPAYMENTS_BASE_URL}/currencies",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Filter to only include our supported cryptocurrencies
                        currencies = [c for c in data["currencies"] if c in SUPPORTED_CRYPTOS]
                        return currencies
                    else:
                        logger.error(f"Failed to get currencies: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error getting currencies: {str(e)}")
            return []
    
    async def get_exchange_rates(self, currency_from, currency_to="USD"):
        """Get exchange rate for a specific cryptocurrency to USD"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{NOWPAYMENTS_BASE_URL}/estimate?amount=1&currency_from={currency_from}&currency_to={currency_to}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["estimated_amount"]
                    else:
                        logger.error(f"Failed to get exchange rate: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting exchange rate: {str(e)}")
            return None
    
    async def create_payment(self, price_amount, price_currency="USD", pay_currency=None, order_id=None, order_description=None, success_url=None, cancel_url=None):
        """Create a payment in NOWPayments"""
        try:
            payload = {
                "price_amount": price_amount,
                "price_currency": price_currency,
                "ipn_callback_url": os.getenv("NOWPAYMENTS_IPN_URL", f"{os.getenv('WEBHOOK_URL', 'https://your-domain.com')}/webhook/nowpayments"),
                "order_id": order_id or f"order_{datetime.now().timestamp()}",
                "order_description": order_description or "Deposit to Gamble Bot"
            }
            
            # If specific payment currency is requested
            if pay_currency:
                payload["pay_currency"] = pay_currency
                
            # Add success and cancel URLs if provided
            if success_url:
                payload["success_url"] = success_url
            if cancel_url:
                payload["cancel_url"] = cancel_url
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{NOWPAYMENTS_BASE_URL}/payment",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create payment: {response.status}, {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return None
    
    async def get_payment_status(self, payment_id):
        """Get status of a payment"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{NOWPAYMENTS_BASE_URL}/payment/{payment_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Failed to get payment status: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return None
    
    async def get_payments(self, limit=10, page=0, sort_by="created_at", order_by="desc", date_from=None, date_to=None):
        """Get list of payments"""
        try:
            params = {
                "limit": limit,
                "page": page,
                "sortBy": sort_by,
                "orderBy": order_by
            }
            
            if date_from:
                params["dateFrom"] = date_from
            if date_to:
                params["dateTo"] = date_to
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{NOWPAYMENTS_BASE_URL}/payment",
                    headers=self.headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Failed to get payments: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting payments: {str(e)}")
            return None
    
    async def create_invoice(self, price_amount, price_currency="USD", order_id=None, order_description=None, success_url=None, cancel_url=None):
        """Create an invoice"""
        try:
            payload = {
                "price_amount": price_amount,
                "price_currency": price_currency,
                "ipn_callback_url": os.getenv("NOWPAYMENTS_IPN_URL", f"{os.getenv('WEBHOOK_URL', 'https://your-domain.com')}/webhook/nowpayments"),
                "order_id": order_id or f"order_{datetime.now().timestamp()}",
                "order_description": order_description or "Deposit to Gamble Bot"
            }
            
            # Add success and cancel URLs if provided
            if success_url:
                payload["success_url"] = success_url
            if cancel_url:
                payload["cancel_url"] = cancel_url
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{NOWPAYMENTS_BASE_URL}/invoice",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create invoice: {response.status}, {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            return None
    
    async def create_withdrawal(self, address, currency, amount, extra_id=None):
        """Create a withdrawal request"""
        try:
            payload = {
                "address": address,
                "currency": currency,
                "amount": amount
            }
            
            if extra_id:
                payload["extra_id"] = extra_id
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{NOWPAYMENTS_BASE_URL}/withdrawal",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create withdrawal: {response.status}, {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error creating withdrawal: {str(e)}")
            return None
    
    async def get_min_payment_amount(self, currency_from, currency_to="USD"):
        """Get minimum payment amount for a cryptocurrency"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{NOWPAYMENTS_BASE_URL}/min-amount?currency_from={currency_from}&currency_to={currency_to}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["min_amount"]
                    else:
                        logger.error(f"Failed to get min amount: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting min amount: {str(e)}")
            return None
            
    async def get_available_balance(self):
        """Get available balance for withdrawals"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{NOWPAYMENTS_BASE_URL}/balance",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["availableBalance"]
                    else:
                        logger.error(f"Failed to get balance: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return None

# Create a global instance of the API client
nowpayments_client = NOWPaymentsAPI()

# Helper functions for common operations
async def get_api_status():
    """Check if the NOWPayments API is operational with enhanced logging"""
    logger.debug("Checking NOWPayments API status")
    
    try:
        status = await nowpayments_client.get_status()
        
        if status:
            api_message = status.get("message", "unknown")
            logger.info(f"NOWPayments API status: {api_message}")
        else:
            logger.warning("NOWPayments API status check returned None")
        
        return status
        
    except Exception as e:
        logger.error(f"Error checking NOWPayments API status: {str(e)}", exc_info=True)
        return None

async def get_crypto_price(crypto_currency, fiat_currency="USD"):
    """Get the current price of a cryptocurrency in USD"""
    rate = await nowpayments_client.get_exchange_rates(crypto_currency, fiat_currency)
    return rate

async def create_deposit_payment(user_id, amount_usd, crypto_currency=None):
    """Create a direct payment for a user with enhanced logging"""
    order_id = f"deposit_{user_id}_{datetime.now().timestamp()}"
    order_description = f"Deposit {amount_usd} USD to ExoWin Bot wallet"
    
    logger.info(f"Creating payment for user {user_id}: ${amount_usd} USD in {crypto_currency}")
    
    try:
        payment = await nowpayments_client.create_payment(
            price_amount=amount_usd,
            price_currency="USD",
            pay_currency=crypto_currency,
            order_id=order_id,
            order_description=order_description
        )
        
        if payment:
            logger.info(f"Payment created successfully: {payment.get('payment_id', 'unknown_id')}")
        else:
            logger.error(f"Payment creation returned None for user {user_id}")
        
        return payment
        
    except Exception as e:
        logger.error(f"Error creating payment for user {user_id}: {str(e)}", exc_info=True)
        return None

async def create_deposit_invoice(user_id, amount_usd):
    """Create a multi-currency invoice for a user"""
    order_id = f"deposit_{user_id}_{datetime.now().timestamp()}"
    order_description = f"Deposit {amount_usd} USD to Gamble Bot wallet"
    
    invoice = await nowpayments_client.create_invoice(
        price_amount=amount_usd,
        price_currency="USD",
        order_id=order_id,
        order_description=order_description
    )
    
    return invoice

async def check_payment_status(payment_id):
    """Check the status of a payment with enhanced logging"""
    logger.debug(f"Checking status for payment: {payment_id}")
    
    try:
        status = await nowpayments_client.get_payment_status(payment_id)
        
        if status:
            payment_status = status.get("payment_status", "unknown")
            logger.info(f"Payment {payment_id} status: {payment_status}")
        else:
            logger.warning(f"No status returned for payment: {payment_id}")
        
        return status
        
    except Exception as e:
        logger.error(f"Error checking payment status for {payment_id}: {str(e)}", exc_info=True)
        return None

async def get_recent_payments(limit=10):
    """Get recent payments"""
    payments = await nowpayments_client.get_payments(limit=limit)
    return payments

async def process_withdrawal(user_id, address, crypto_currency, amount_crypto, extra_id=None):
    """Process a withdrawal request"""
    withdrawal = await nowpayments_client.create_withdrawal(
        address=address,
        currency=crypto_currency,
        amount=amount_crypto,
        extra_id=extra_id
    )
    
    return withdrawal

async def get_minimum_deposit_amount(crypto_currency):
    """Get the minimum deposit amount for a cryptocurrency"""
    min_amount = await nowpayments_client.get_min_payment_amount(crypto_currency)
    return min_amount

async def get_wallet_balance():
    """Get the available balance in the NOWPayments wallet"""
    balance = await nowpayments_client.get_available_balance()
    return balance

# IPN (Instant Payment Notification) handler
async def verify_ipn_request(request_data, signature_header):
    """Verify the authenticity of an IPN request"""
    import hmac
    import hashlib
    
    if not NOWPAYMENTS_IPN_SECRET:
        logger.error("IPN secret is not set")
        return False
    
    # Sort the request data
    sorted_data = json.dumps(request_data, separators=(',', ':'), sort_keys=True)
    
    # Create HMAC signature
    signature = hmac.new(
        NOWPAYMENTS_IPN_SECRET.encode('utf-8'),
        sorted_data.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()
    
    # Compare signatures
    return signature == signature_header

async def handle_ipn_notification(request_data, signature_header):
    """Handle IPN notification from NOWPayments"""
    from src.database import update_user_balance, record_transaction
    
    # Verify the request
    if not await verify_ipn_request(request_data, signature_header):
        logger.error("Invalid IPN signature")
        return False
    
    # Process the payment notification
    payment_status = request_data.get("payment_status")
    order_id = request_data.get("order_id", "")
    
    # Check if this is a deposit
    if order_id.startswith("deposit_"):
        parts = order_id.split("_")
        if len(parts) >= 2:
            try:
                user_id = int(parts[1])
                
                # If payment is confirmed
                if payment_status == "confirmed" or payment_status == "finished":
                    price_amount = float(request_data.get("price_amount", 0))
                    
                    # Credit the user's account
                    await update_user_balance(user_id, price_amount)
                    await record_transaction(
                        user_id, 
                        price_amount, 
                        "deposit", 
                        details={
                            "payment_id": request_data.get("payment_id"),
                            "currency": request_data.get("pay_currency"),
                            "crypto_amount": request_data.get("pay_amount")
                        }
                    )
                    
                    logger.info(f"Deposit of {price_amount} USD credited to user {user_id}")
                    return True
            except (ValueError, Exception) as e:
                logger.error(f"Error processing IPN: {str(e)}")
    
    return False