from Tendering.utils.fcm import send_fcm_notification
from Tendering.models import Notification

def trigger_notification(recipient, sender, n_type, message, tender, bid=None):
    notif = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=n_type,
        message=message,
        tender=tender,
        tender_title=tender.title,
        bid_title=bid.title if bid else "N/A"
    )

    if hasattr(recipient, 'fcm_token') and recipient.fcm_token:
        try:
            send_fcm_notification(
                token=recipient.fcm_token,
                title="TenderingDU",
                body=message,
                data={
                    "type": n_type,
                    "tender_id": str(tender.id),
                    "bid_id": str(bid.id) if bid else ""
                }
            )
        except Exception as e:
            print(f"FCM Error: {e}")