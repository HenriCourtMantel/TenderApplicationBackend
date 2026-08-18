from firebase_admin.messaging import UnregisteredError
from Tendering.utils.fcm import send_fcm_notification 
from Tendering.models import Notification
def trigger_notification(recipient, sender, n_type, message, tender=None, bid=None):
    print(f" NOTIFICATION RECIPIENT: {recipient.email}")
    print(f" RECIPIENT FCM TOKEN: {recipient.fcm_token}")

    notif = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=n_type,
        message=message,
        tender=tender,
        tender_title=tender.title if tender else "N/A",
        bid_title=bid.title if bid else "N/A"
    )

    if hasattr(recipient, 'fcm_token') and recipient.fcm_token:
        try:
            res = send_fcm_notification(
                token=recipient.fcm_token,
                title="TenderingDU",
                body=message,
                data={
                    "type": n_type,
                    "tender_id": str(tender.id) if tender else "",
                    "bid_id": str(bid.id) if bid else ""
                }
            )
            print(f" FIREBASE PUSH RESPONSE ID: {res}")
        except Exception as e:
            print(f" FCM ERROR: {e}")
    else:
        print("SKIPPED: Recipient has NO fcm_token saved!")

    return notif