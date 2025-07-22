# accounts/middleware.py
from django.utils import timezone
class AutoUnbanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = request.user.profile
            if profile.is_banned and profile.ban_expiry and timezone.now() > profile.ban_expiry:
                profile.is_banned = False
                profile.ban_expiry = None
                profile.strike_count = 0  # Reset strikes
                profile.save()
        return self.get_response(request)