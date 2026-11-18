"""
generate_dataset.py
--------------------
Generates a synthetic but realistic labeled dataset of phishing/scam and
legitimate messages across three channels: Email, SMS, and UPI payment
requests. This is used to train the scam-detection ML model.

In a production system you would replace this with a real labeled dataset
(e.g. from Kaggle's SMS Spam Collection, PhishTank, or your own UPI fraud
logs). This generator exists so the project is runnable end-to-end without
any external downloads.

Run:
    python generate_dataset.py
Produces:
    dataset.csv  (columns: text, channel, label)   label: 1 = scam, 0 = legit
"""

import csv
import random

random.seed(42)

# ---------------------------------------------------------------------------
# SCAM (label = 1) message templates
# ---------------------------------------------------------------------------
phishing_email_templates = [
    "Dear customer, your account has been suspended. Click here to verify your identity immediately: {link}",
    "URGENT: Your bank account will be locked in 24 hours. Update your KYC details now at {link}",
    "Congratulations! You have won a lottery of Rs {amount}. Claim your prize by clicking {link}",
    "Your Netflix subscription payment failed. Update your billing information here: {link}",
    "Security Alert: Unusual sign-in activity detected. Confirm your password at {link}",
    "Your parcel could not be delivered. Pay a customs fee of Rs {amount} at {link} to release it",
    "Dear user, your PAN card will be deactivated. Verify now to avoid penalty: {link}",
    "Final notice: Your electricity connection will be disconnected tonight. Pay now at {link}",
    "You have an unclaimed refund of Rs {amount} from Income Tax Department. Claim here: {link}",
    "Your Amazon account has been compromised. Reset your password immediately: {link}",
    "Job offer! Work from home and earn Rs {amount} per day. Register now at {link}",
    "Your credit card has been blocked due to suspicious activity. Verify at {link} to unblock",
    "Free recharge of Rs {amount} waiting for you! Click {link} before offer expires",
    "Your document is ready for e-KYC verification, click {link} to avoid account suspension",
]

phishing_sms_templates = [
    "Your a/c XXXX will be blocked today. Update KYC immediately: {link}",
    "You won Rs {amount} cashback! Claim now {link} Offer valid 30 mins only",
    "Dear customer your SBI account is suspended, click {link} to reactivate",
    "URGENT: OTP shared with unknown number, verify identity now {link}",
    "Your electricity bill of Rs {amount} is pending, pay now to avoid disconnection {link}",
    "Congrats! You are selected for a free iPhone. Claim at {link} now",
    "Your parcel is on hold, pay Rs {amount} customs duty at {link}",
    "Last warning: Your mobile number will be deactivated. Verify at {link}",
    "Your loan of Rs {amount} is pre-approved, apply now {link} limited slots",
    "KYC pending for your account, complete now or account will be blocked {link}",
]

phishing_upi_templates = [
    "You have received a payment request of Rs {amount} from unknown@upi. Approve to receive money at {link}",
    "Your KYC for UPI has expired. Update immediately to avoid deactivation: {link}",
    "Scan this QR to receive Rs {amount} cashback into your UPI account {link}",
    "Dear user, a refund of Rs {amount} is pending. Approve the collect request to receive it",
    "Your UPI PIN needs to be reset due to security breach, click {link} to reset",
    "Get Rs {amount} instantly by accepting this payment request on GPay/PhonePe {link}",
    "Your UPI ID will be blocked in 2 hours, verify now to continue using UPI {link}",
    "Cashback of Rs {amount} credited, click on collect request to claim it now",
    "Complete your UPI account merger by approving the request sent to your number {link}",
    "Your bank has sent a payment collect request for Rs 1 verification, approve to activate account",
]

# ---------------------------------------------------------------------------
# LEGITIMATE (label = 0) message templates
# ---------------------------------------------------------------------------
legit_email_templates = [
    "Hi, just confirming our meeting scheduled for {day} at {time}. Let me know if that works.",
    "Your order #{amount} has been shipped and will arrive in 3-5 business days.",
    "Thank you for subscribing to our monthly newsletter. Here are this month's updates.",
    "Please find attached the invoice for services rendered in the month of {day}.",
    "Reminder: Your appointment with Dr. Sharma is on {day} at {time}.",
    "Your monthly statement for account ending 4321 is now available in your account portal.",
    "Team, please review the attached project report before tomorrow's stand-up meeting.",
    "Welcome to our platform! Here's how to get started with your new account.",
    "Your flight booking is confirmed. Boarding starts at {time} on {day}.",
    "This is a receipt for your recent purchase. Thank you for shopping with us.",
    "Hey, are we still on for lunch on {day}? Let me know your preferred time.",
    "The quarterly performance review is scheduled for {day}, please prepare your reports.",
]

legit_sms_templates = [
    "Your OTP for login is 482913. Do not share this with anyone. Valid for 10 minutes.",
    "Your order has been delivered. Thank you for shopping with us.",
    "Reminder: Your electricity bill of Rs {amount} is due on {day}. Pay via official app only.",
    "Your appointment with the doctor is confirmed for {day} at {time}.",
    "Hi, this is a reminder that your subscription renews on {day}.",
    "Your cab is arriving in 5 minutes. Driver contact: 98XXXXXXXX",
    "Thank you for your payment of Rs {amount}. Your account balance is updated.",
    "Your exam admit card is now available for download on the college portal.",
    "Meeting rescheduled to {time} on {day}, please confirm your availability.",
    "Your monthly attendance report has been generated, check the college app.",
]

legit_upi_templates = [
    "You have successfully sent Rs {amount} to Rahul via UPI. Reference No: 24839201.",
    "Rs {amount} has been credited to your account from Priya Sharma via UPI.",
    "Your UPI transaction of Rs {amount} to Electricity Board was successful.",
    "Payment of Rs {amount} to Swiggy was successful. Order will arrive in 30 minutes.",
    "You paid Rs {amount} to Local Grocery Store via UPI. Thank you.",
    "Rs {amount} debited from your account for movie tickets booking via UPI.",
    "Split bill request from Amit for Rs {amount} for dinner. Review in your UPI app.",
    "Your UPI mandate for monthly rent of Rs {amount} has been set up successfully.",
]

def rand_link():
    domains = ["bit.ly/verify-now", "secure-kyc-update.com", "acc0unt-verify.in",
               "claim-reward.net", "verify-bank-online.co", "upi-refund-portal.com"]
    return "http://" + random.choice(domains) + "/" + str(random.randint(1000, 9999))

def rand_amount():
    return random.choice([49, 99, 199, 499, 999, 1500, 2500, 5000, 10000, 25000, 50000])

def rand_day():
    return random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "next week"])

def rand_time():
    return random.choice(["9:00 AM", "11:30 AM", "2:00 PM", "4:30 PM", "6:00 PM"])

def fill(template):
    return template.format(
        link=rand_link(), amount=rand_amount(), day=rand_day(), time=rand_time()
    )

def build_rows():
    rows = []
    groups = [
        (phishing_email_templates, "email", 1),
        (phishing_sms_templates, "sms", 1),
        (phishing_upi_templates, "upi", 1),
        (legit_email_templates, "email", 0),
        (legit_sms_templates, "sms", 0),
        (legit_upi_templates, "upi", 0),
    ]
    # Repeat + randomize placeholders to get a reasonably sized dataset
    for templates, channel, label in groups:
        for _ in range(25):
            template = random.choice(templates)
            rows.append((fill(template), channel, label))
    random.shuffle(rows)
    return rows

if __name__ == "__main__":
    rows = build_rows()
    with open("dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "channel", "label"])
        writer.writerows(rows)
    print(f"Generated {len(rows)} rows -> dataset.csv")
