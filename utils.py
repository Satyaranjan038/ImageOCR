import fitz  # PyMuPDF
import re

def extract_pdf_details(file_path, password=''):
    # Open the PDF file
    doc = fitz.open(file_path)

    # Attempt to unlock the document if it's password-protected
    if doc.needs_pass:
        if not doc.authenticate(password):
            return {"error": "Invalid password or unable to unlock PDF."}

    details = []

    # Regular expressions to match the data
    date_pattern = re.compile(r'\b[A-Za-z]{3} \d{2}, \d{4}\b')
    amount_pattern = re.compile(r'INR [\d,]+(\.\d{1,2})?')  # Adjusted to handle commas
    transaction_pattern = re.compile(r'(Paid to|Received from)')

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        lines = text.splitlines()

        current_detail = {}
        capture_amount = False

        for line in lines:
            # Extract Date
            date_match = date_pattern.search(line)
            if date_match:
                current_detail['date'] = date_match.group()

            # Extract "Paid to" or "Received from" information
            transaction_match = transaction_pattern.search(line)
            if transaction_match:
                if "Paid to" in line:
                    current_detail['transaction_type'] = "Debit"
                    current_detail['party'] = line.split("Paid to")[1].strip()
                    capture_amount = True
                elif "Received from" in line:
                    current_detail['transaction_type'] = "Credit"
                    current_detail['party'] = line.split("Received from")[1].strip()
                    capture_amount = True

            # Extract Amount
            if capture_amount:
                amount_match = amount_pattern.search(line)
                if amount_match:
                    amount_str = amount_match.group()
                    formatted_amount = amount_str.replace('INR', '').replace(',', '').strip()
                    current_detail['amount'] = formatted_amount
                    capture_amount = False

            # If all details are collected, save and reset the current detail dictionary
            if 'date' in current_detail and 'transaction_type' in current_detail and 'party' in current_detail and 'amount' in current_detail:
                details.append(current_detail)
                current_detail = {}

    return {
        "transactions": details
    }


def extract_pdf_details_android(file_path, password=''):
    # Open the PDF file
    doc = fitz.open(file_path)

    # Attempt to unlock the document if it's password-protected
    if doc.needs_pass:
        if not doc.authenticate(password):
            return {"error": "Invalid password or unable to unlock PDF."}

    details = []

    # Regular expressions to match the data
    date_pattern = re.compile(r'\b[A-Za-z]{3} \d{2}, \d{4}\b')
    amount_pattern = re.compile(r'₹[\d,]+(\.\d{1,2})?')  # Matches amount with ₹ symbol and handles commas

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        lines = text.splitlines()

        current_detail = {}

        for line in lines:
            # Extract Date
            date_match = date_pattern.search(line)
            if date_match:
                current_detail['date'] = date_match.group()

            # Extract "Paid to" or "Received from" information
            if "Paid to" in line:
                current_detail['transaction_type'] = "Debit"
                current_detail['party'] = line.split("Paid to")[1].strip()
            elif "Received from" in line:
                current_detail['transaction_type'] = "Credit"
                current_detail['party'] = line.split("Received from")[1].strip()

            # Extract Amount
            amount_match = amount_pattern.search(line)
            if amount_match:
                amount_str = amount_match.group()
                # Convert the amount to the required format "INR xx.xx"
                formatted_amount = "INR " + amount_str.replace('₹', '').replace(',', '').strip()
                current_detail['amount'] = formatted_amount

            # Extract Transaction ID
            if 'Transaction ID' in line:
                current_detail['transaction_id'] = line.split("Transaction ID")[1].strip()

            # If all details are collected, save and reset the current detail dictionary
            if 'date' in current_detail and 'transaction_type' in current_detail and 'party' in current_detail and 'amount' in current_detail:
                details.append(current_detail)
                current_detail = {}

    return {
        "transactions": details
    }
