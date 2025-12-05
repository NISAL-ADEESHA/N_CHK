import hashlib
import random
from datetime import datetime

class CarnageGateway:
    """Carnage Payment Gateway Checker (Admin Only) - $5 Charge"""
    
    @staticmethod
    def check_gateway_status():
        """Check if Carnage gateway is accessible"""
        try:
            # Simulating gateway status check
            statuses = ['🟢 Online', '🟡 Maintenance', '🔴 Offline']
            status = random.choice(statuses)
            return {
                'gateway': 'Carnage',
                'status': status,
                'accessible': status == '🟢 Online',
                'last_checked': datetime.now().strftime('%H:%M:%S')
            }
        except Exception as e:
            return {
                'gateway': 'Carnage',
                'status': '🔴 Error',
                'accessible': False,
                'error': str(e)
            }
    
    @staticmethod
    def test_card(card_details: str, amount: float = 5.0):
        """
        Test a card on Carnage gateway - ADMIN ONLY
        Format: CC|MM|YY|CVV
        $5 Charge Amount
        """
        try:
            cc, mm, yy, cvv = card_details.split('|')
            
            # Extract BIN info
            bin_info = {
                "brand": "Visa" if cc.startswith('4') else 
                        "Mastercard" if cc.startswith('5') else 
                        "Amex" if cc.startswith('3') else 
                        "Discover" if cc.startswith('6') else "Other",
                "type": "Credit/Debit",
                "bank": "International Gateway",
                "country": "US",
                "bin": cc[:6]
            }
            
            # Simulate various responses for $5 charge
            responses = [
                ("Approved", f"${amount:.2f} Charge Successful", "200"),
                ("Declined", "Insufficient Funds", "201"),
                ("Declined", "Invalid Card", "202"),
                ("Declined", "Bank Rejected", "203"),
                ("Approved", f"${amount:.2f} Pre-authorization OK", "204")
            ]
            
            # Use card hash for consistent results
            card_hash = int(hashlib.md5(card_details.encode()).hexdigest()[:8], 16)
            response_idx = card_hash % len(responses)
            
            status, message, code = responses[response_idx]
            
            return {
                "status": status,
                "message": message,
                "response_code": code,
                "amount": amount,
                "currency": "USD",
                "gateway": "Carnage Payment Gateway",
                **bin_info
            }
            
        except Exception as e:
            return {
                "status": "Error",
                "message": f"Processing error: {str(e)}",
                "gateway": "Carnage Payment Gateway"
            }