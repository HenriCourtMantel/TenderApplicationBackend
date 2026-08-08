import os
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

if not firebase_admin._apps:
    if os.path.exists(settings.FIREBASE_CONFIG_PATH):
        try:
            cred = credentials.Certificate(settings.FIREBASE_CONFIG_PATH)
            firebase_admin.initialize_app(cred)
            print("Firebase successfully initialized.")
        except Exception as e:
            print(f"Failed to initialize Firebase: {e}")
    else:
        print(f"WARNING: Firebase config file not found at {settings.FIREBASE_CONFIG_PATH}. Push notifications will not work.")

def send_fcm_notification(token, title, body, data=None):
    if not token or not firebase_admin._apps:
        return None
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        data=data or {},
        token=token,
    )
    return messaging.send(message)