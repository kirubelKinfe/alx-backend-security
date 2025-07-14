from django.utils import timezone
from ip_tracking.models import RequestLog

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract IP address (check HTTP_X_FORWARDED_FOR for proxies, fallback to REMOTE_ADDR)
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            # Take the first IP in case of multiple IPs in the forwarded header
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '')

        # Get request path and current timestamp
        path = request.path
        timestamp = timezone.now()

        # Create and save RequestLog instance
        try:
            RequestLog.objects.create(
                ip_address=ip_address,
                timestamp=timestamp,
                path=path
            )
        except Exception as e:
            # Handle potential database errors silently to avoid disrupting request processing
            pass

        # Process the request and return the response
        response = self.get_response(request)
        return response