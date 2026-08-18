import os
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

def initialize_firebase():
    if not firebase_admin._apps:
        config_path = getattr(settings, 'FIREBASE_CONFIG_PATH', None)
        print(f"DEBUG: FIREBASE_CONFIG_PATH = {config_path}")
        
        if config_path and os.path.exists(config_path):
            try:
                cred = credentials.Certificate(config_path)
                firebase_admin.initialize_app(cred)
                print(" Firebase successfully initialized!")
            except Exception as e:
                print(f" Failed to initialize Firebase: {e}")
        else:
            print(f" ERROR: Config file does NOT exist at path: {config_path}")

def send_fcm_notification(token, title, body, data=None):
    initialize_firebase()

    if not token:
        print(" FCM ERROR: No token provided!")
        return None

    if not firebase_admin._apps:
        print(" FCM ERROR: firebase_admin._apps is still empty after initialization!")
        return None

    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=token,
        )
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f" FCM Exception inside messaging.send: {e}")
        return None