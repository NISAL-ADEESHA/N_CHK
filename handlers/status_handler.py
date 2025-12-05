from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from gateways.stripe_checker import StripeChecker
from gateways.slt_checker import SLTChecker
from gateways.carnage_checker import CarnageGateway
from datetime import datetime

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check all gateway statuses"""
    msg = await update.message.reply_text("🔍 Checking all gateway statuses...")
    
    # Check all gateway statuses
    stripe_status = StripeChecker.check_gateway_status()
    slt_status = SLTChecker.check_gateway_status()
    carnage_status = CarnageGateway.check_gateway_status()
    
    # Build status message
    txt = "📊 **GATEWAY STATUS OVERVIEW**\n\n"
    
    # Stripe Status
    txt += f"**💳 Stripe Payment Gateway:**\n"
    txt += f"Status: {stripe_status['status']}\n"
    
    if stripe_status['accessible']:
        txt += f"• API Endpoint: ✅ Accessible\n"
        txt += f"• JS Library: ✅ Accessible\n"
        txt += f"• Checkout: ✅ Accessible\n"
    else:
        txt += f"• Status: 🔴 Unavailable\n"
    
    txt += "\n"
    
    # SLT Status
    txt += f"**🏦 SLT Mastercard Gateway:**\n"
    txt += f"Status: {slt_status['status']}\n"
    
    if slt_status['accessible']:
        for detail in slt_status['details']:
            status_icon = "✅" if detail['accessible'] else "❌"
            endpoint_name = detail['url'].split('/')[-1]
            txt += f"• {endpoint_name}: {status_icon} (HTTP {detail['status']})\n"
    else:
        txt += f"• Status: 🔴 Unavailable\n"
    
    txt += "\n"
    
    # Carnage Status
    txt += f"**🔪 Carnage Payment Gateway:**\n"
    txt += f"Status: {carnage_status['status']}\n"
    txt += f"• Charge Amount: $5.00\n"
    txt += f"• Last Checked: {carnage_status.get('last_checked', 'N/A')}\n"
    
    # CG 0.5 Status
    txt += "\n"
    txt += f"**💰 CG 0.5 Donation Gateway:**\n"
    txt += f"Status: 🟢 Online\n"
    txt += f"• Charge Amount: $0.50\n"
    txt += f"• Gateway: Donation Website\n"
    
    # Overall Status
    txt += "\n**🔍 Overall Status:**\n"
    online_gateways = sum([
        stripe_status['accessible'],
        slt_status['accessible'],
        carnage_status['accessible']
    ]) + 1  # +1 for CG 0.5 which is always online in simulation
    
    if online_gateways == 4:
        txt += "🟢 All gateways are online and operational\n"
    elif online_gateways >= 3:
        txt += "🟡 Most gateways are online\n"
    elif online_gateways >= 2:
        txt += "🟡 Some gateways are online\n"
    else:
        txt += "🔴 All gateways are offline\n"
    
    txt += f"\n🔄 Last Checked: {datetime.now().strftime('%H:%M:%S')}\n"
    txt += f"👨‍💻 *NeuroSnare Checker*"
    
    await msg.edit_text(txt, parse_mode=ParseMode.MARKDOWN)