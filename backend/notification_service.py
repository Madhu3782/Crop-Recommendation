def send_alert(contact, message):
    # In a real app, this would send SMS/Email via Twilio/SendGrid
    print(f"\n[NOTIFICATION SERVICE] Sending to {contact}: {message}\n", flush=True)
    return True
