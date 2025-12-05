import random
import time
import os
from datetime import datetime

def generate_random_cc(bin_pattern, amount=10, exp_month=None, exp_year=None, cvv=None):
    """Generate cards with custom parameters"""
    cards = []
    
    card_brands = {
        "4": (16, "Visa"),
        "5": (16, "Mastercard"),
        "34": (15, "Amex"),
        "37": (15, "Amex"),
        "6": (16, "Discover")
    }
    
    for _ in range(amount):
        card_length = 16
        for prefix, (length, brand) in card_brands.items():
            if bin_pattern.startswith(prefix):
                card_length = length
                break
        
        # Generate card number
        card_number = bin_pattern
        while len(card_number) < card_length - 1:
            card_number += str(random.randint(0, 9))
        
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10

        def calculate_luhn(partial_card_num):
            check_digit = luhn_checksum(partial_card_num + '0')
            return str((10 - check_digit) % 10)
        
        card_number += calculate_luhn(card_number)
        
        # Use custom or random expiration
        if exp_month:
            exp_m = exp_month
        else:
            exp_m = random.randint(1, 12)
            
        if exp_year:
            exp_y = exp_year
        else:
            current_year = datetime.now().year
            exp_y = random.randint(current_year, current_year + 5)
        
        # Use custom or random CVV
        if cvv:
            card_cvv = cvv
        else:
            if bin_pattern.startswith(('34', '37')):
                card_cvv = str(random.randint(1000, 9999))
            else:
                card_cvv = str(random.randint(100, 999))
        
        card = f"{card_number}|{exp_m:02d}|{exp_y}|{card_cvv}"
        cards.append(card)
    
    return cards

def create_cc_file(cards, filename="cc.txt"):
    """Create a text file with generated cards"""
    with open(filename, 'w', encoding='utf-8') as f:
        for card in cards:
            f.write(f"{card}\n")
    return filename

def parse_card_parameters(input_string):
    """Parse user input to extract BIN, month, year, CVV from various formats"""
    input_string = input_string.strip()
    parts = input_string.split('|')
    
    if len(parts) >= 4:
        bin_pattern = parts[0].strip()
        exp_month = parts[1].strip() if parts[1].strip() else None
        exp_year = parts[2].strip() if parts[2].strip() else None
        cvv = parts[3].strip() if len(parts) > 3 and parts[3].strip() else None
        
        try:
            if exp_month: exp_month = int(exp_month)
            if exp_year: exp_year = int(exp_year)
        except ValueError:
            pass
            
        return bin_pattern, exp_month, exp_year, cvv
    elif len(parts) == 2 and parts[1].isdigit() and len(parts[1]) in [3, 4]:
        bin_pattern = parts[0].strip()
        cvv = parts[1].strip()
        return bin_pattern, None, None, cvv
    elif len(parts) == 2 and (parts[1].isdigit() and 1 <= len(parts[1]) <= 2):
        bin_pattern = parts[0].strip()
        exp_month = parts[1].strip()
        try:
            if exp_month: exp_month = int(exp_month)
        except ValueError:
            exp_month = None
        return bin_pattern, exp_month, None, None
    else:
        clean_bin = ''.join(filter(str.isdigit, input_string))
        if 6 <= len(clean_bin) <= 19:
            return clean_bin, None, None, None
        else:
            return input_string, None, None, None