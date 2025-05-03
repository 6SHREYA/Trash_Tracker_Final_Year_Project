from twilio.rest import Client
import datetime
import sys

# Twilio Credentials
SID = 'ACe91623fd25f7469c81a0e35add822bc2'
AUTH = 'b68be38bc93812e02fd8399585fb6d82'

# Function to send SMS with error handling
def sms(t1, lat, lon):
    try:
        # Create a shortened timestamp (just time, no date)
        if isinstance(t1, datetime.datetime):
            short_time = t1.strftime("%H:%M")
        else:
            short_time = str(t1)
        
        # Create a shortened message body - avoiding long links for trial accounts
        message_body = f"⚠️ Trash Alert! {short_time} @ {lat:.4f},{lon:.4f}"

        client = Client(SID, AUTH)

        message = client.messages.create(
            body=message_body,
            from_='+15513832453',
            to='+919999889373'
        )

        print(f"✅ SMS Message SID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ SMS Error: {e}")
        return False

# Function to send WhatsApp message with error handling
def whatsapp1(lat, lon):
    try:
        client = Client(SID, AUTH)

        # Keep WhatsApp message simple too
        message = client.messages.create(
            body='🚨 Trash Detected!',
            persistent_action=[f'geo:{lat},{lon}|Trash Location'],
            from_='whatsapp:+14155238886',
            to='whatsapp:+919999889373'
        )

        print(f"✅ WhatsApp Message SID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ WhatsApp Error: {e}")
        return False

# Optional: Function to send location link as a separate SMS once account is upgraded
def send_location_link(lat, lon):
    try:
        google_maps_link = f"https://www.google.com/maps/search/?api=1&query={float(lat)},{float(lon)}"
        message_body = f"Location: {google_maps_link}"

        client = Client(SID, AUTH)

        message = client.messages.create(
            body=message_body,
            from_='+15513832453',
            to='+919999889373'
        )

        print(f"✅ Location Link SMS SID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Location Link Error: {e}")
        return False

# Example Usage with additional diagnostic information
if __name__ == "__main__":
    print("Starting notification test...")
    
    # Print Twilio credential info (partial for security)
    print(f"Using SID: {SID[:5]}...{SID[-5:]}")
    print(f"Using AUTH: {AUTH[:2]}...{AUTH[-2:]}")
    
    ct = datetime.datetime.now()
    lat = 12.9719
    lon = 77.5937
    
    print(f"Sending SMS at: {ct}")
    sms_result = sms(ct, lat, lon)
    
    print(f"Sending WhatsApp at: {ct}")
    wa_result = whatsapp1(lat, lon)
    
    if not sms_result and not wa_result:
        print("❌ Both notification methods failed. Please check your Twilio account.")
    elif not sms_result:
        print("❌ SMS failed but WhatsApp succeeded.")
    elif not wa_result:
        print("❌ WhatsApp failed but SMS succeeded.")
    else:
        print("✅ All notifications sent successfully!")
        
    # Uncomment the following line after upgrading Twilio account
    # send_location_link(lat, lon)