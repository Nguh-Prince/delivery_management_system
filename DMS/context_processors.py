from django.contrib.auth.models import AnonymousUser
from .models import Notification
def unread_notifications_count(request):
    if isinstance(request.user, AnonymousUser):
        return {
            'unread_notifications_count': 0  # Or handle it in a way that suits your application
        }
    else:
        unread_count = Notification.objects.filter(sender=request.user, read=False).count()
        return {
            'unread_notifications_count': unread_count
        }
