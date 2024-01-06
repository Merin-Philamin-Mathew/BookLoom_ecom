""" # Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = "ACfb492540469efa4ae2061f14b0bbca71"
auth_token = "aceccb974555b18c1a21b19f23c0e414"
verify_sid = "VA0b654098fa34414d86d3e2447fc1568d"
verified_number = "+918281809934"

client = Client(account_sid, auth_token)

verification = client.verify.v2.services(verify_sid) \
  .verifications \
  .create(to=verified_number, channel="sms")
print(verification.status)

otp_code = input("Please enter the OTP:")

verification_check = client.verify.v2.services(verify_sid) \
  .verification_checks \
  .create(to=verified_number, code=otp_code)
print(verification_check.status) """