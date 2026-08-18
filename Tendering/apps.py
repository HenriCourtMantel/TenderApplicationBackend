import os
import firebase_admin
from firebase_admin import credentials
from django.apps import AppConfig
from django.conf import settings

class TenderingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Tendering'

    def ready(self):
        if not firebase_admin._apps:
            cred_path = getattr(settings, 'FIREBASE_CONFIG_PATH', None)
            if cred_path and os.path.exists(cred_path):
                try:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    print(" FIREBASE ADMIN SDK SUCCESSFULLY INITIALIZED IN DJANGO!")
                except Exception as e:
                    print(f" Failed to initialize Firebase Admin: {e}")
            else:
                print(f" WARNING: FIREBASE_CONFIG_PATH not found or invalid at: {cred_path}")