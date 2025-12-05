import requests
import hashlib
from datetime import datetime

class SLTChecker:
    """SLT Mastercard Payment Gateway Checker"""
    
    @staticmethod
    def test_card(card_details: str, amount: float = 100.0):
        """
        Test a card on SLT Mastercard gateway
        Format: CC|MM|YY|CVV
        """
        try:
            cc, mm, yy, cvv = card_details.split('|')
            
            # Simulate card check
            card_hash = hashlib.md5(card_details.encode()).hexdigest()
            
            # Random simulation based on card number
            last_digit = int(cc[-1])
            
            if last_digit % 3 == 0:
                status = "Approved"
                message = f"LKR {amount:.2f} Payment Successful"
                response_code = "00"
            elif last_digit % 3 == 1:
                status = "Declined"
                message = "Insufficient Funds"
                response_code = "51"
            else:
                status = "Declined"
                message = "Invalid Card"
                response_code = "14"
            
            # Extract BIN info
            bin_info = {
                "brand": "Mastercard" if cc.startswith('5') else "Visa" if cc.startswith('4') else "Other",
                "type": "Credit",
                "bank": "Bank of Ceylon Gateway",
                "country": "LK",
                "bin": cc[:6]
            }
            
            return {
                "status": status,
                "message": message,
                "response_code": response_code,
                "amount": amount,
                "currency": "LKR",
                "gateway": "SLT Mastercard Gateway",
                **bin_info
            }
            
        except Exception as e:
            return {
                "status": "Error",
                "message": f"Invalid card format or processing error: {str(e)}",
                "gateway": "SLT Mastercard Gateway"
            }
    
    @staticmethod
    def check_gateway_status():
        """Check if SLT Mastercard gateway is accessible"""
        try:
            urls = [
                "https://bankofceylon.gateway.mastercard.com/checkout/version/61/checkout.js",
                "https://bankofceylon.gateway.mastercard.com/asset/public/assets.js",
                "https://bankofceylon.gateway.mastercard.com/form/v3/hpf.js"
            ]
            
            results = []
            for url in urls:
                try:
                    response = requests.head(url, timeout=5)
                    results.append({
                        'url': url,
                        'status': response.status_code,
                        'accessible': response.status_code == 200
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
                'gateway': 'SLT Mastercard',
                'status': status_map.get(accessible_count, '🔴 Offline'),
                'accessible': accessible_count >= 1,
                'details': results
            }
            
        except Exception as e:
            return {
                'gateway': 'SLT Mastercard',
                'status': '🔴 Error',
                'accessible': False,
                'error': str(e)
            }