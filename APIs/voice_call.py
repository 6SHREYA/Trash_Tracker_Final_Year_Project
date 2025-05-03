from twilio.rest import Client
import time

# Twilio credentials
account_sid = 'ACe91623fd25f7469c81a0e35add822bc2'
auth_token = 'b68be38bc93812e02fd8399585fb6d82'

def make_voice_call(to_number):
    """
    Makes a call with a custom message using Twilio
    
    Args:
        to_number: The phone number to call (with country code)
    """
    try:
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Create TwiML without emojis - just plain text
        # Add pauses and voice attributes for better pronunciation
        twiml = """
        <Response>
            <Say voice="woman" language="en-IN">
                Alert! Garbage detected. Immediate action required.
            </Say>
            <Pause length="1"/>
            <Say voice="woman" language="en-IN">
                I repeat, garbage has been detected in your area. 
                Please take action immediately.
            </Say>
        </Response>
        """
        
        # Make the call
        call = client.calls.create(
            twiml=twiml,
            from_='+15513832453',
            to=to_number
        )
        
        print(f"✅ Call initiated! Call SID: {call.sid}")
        return call.sid
        
    except Exception as e:
        print(f"❌ Error making call: {type(e).__name__}: {str(e)}")
        return None

# Function to check call status
def check_call_status(call_sid):
    """
    Checks the status of a call by its SID
    
    Args:
        call_sid: The SID of the call to check
    """
    try:
        client = Client(account_sid, auth_token)
        call = client.calls(call_sid).fetch()
        return call.status
    except Exception as e:
        print(f"❌ Error checking call status: {e}")
        return "unknown"

# Example usage with status check
if __name__ == "__main__":
    recipient = '+919999889373'  # Replace with your verified number
    
    # Make the call
    print(f"Making call to {recipient}...")
    call_sid = make_voice_call(recipient)
    
    if call_sid:
        # Wait and check status a few times
        for _ in range(5):
            time.sleep(5)  # Wait 5 seconds between checks
            status = check_call_status(call_sid)
            print(f"Call status: {status}")
            
            # If call is completed or failed, stop checking
            if status in ['completed', 'failed', 'busy', 'no-answer', 'canceled']:
                break