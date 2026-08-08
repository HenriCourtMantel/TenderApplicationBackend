from firebase_admin.messaging import UnregisteredError
from Tendering.utils.fcm import send_fcm_notification 
from Tendering.models import Notification

def trigger_notification(recipient, sender, n_type, message, tender=None, bid=None):
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
            send_fcm_notification(
                token=recipient.fcm_token,
                title="TenderingDU",
                body=message,
                data={
                    "type": n_type,
                    "tender_id": str(tender.id) if tender else "",
                    "bid_id": str(bid.id) if bid else ""
                }
            )
        except UnregisteredError:
            recipient.fcm_token = None
            recipient.save(update_fields=['fcm_token'])
        except Exception as e:
            print(f"FCM Error for user {recipient.id}: {e}")
            
    return notif