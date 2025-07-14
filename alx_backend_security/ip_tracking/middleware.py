from django.utils import timezone
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django_ip_geolocation import IpGeolocation
from ip_tracking.models import RequestLog, BlockedIP

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

        # Check if IP is blacklisted
        try:
            if BlockedIP.objects.filter(ip_address=ip_address).exists():
                return HttpResponseForbidden("Access denied: IP address is blocked.")
        except Exception:
            # Handle potential database errors silently to avoid disrupting request processing
            pass

        # Get request path and current timestamp
        path = request.path
        timestamp = timezone.now()

        # Check cache for geolocation data
        cache_key = f"geo_{ip_address}"
        geo_data = cache.get(cache_key)
        country = None
        city = None

        if geo_data:
            # Use cached data
            country = geo_data.get('country')
            city = geo_data.get('city')
        else:
            # Fetch geolocation data from API
            try:
                response = IpGeolocation().geolocate(ip_address)
                if response:
                    country = response.get('country_name')
                    city = response.get('city')
                    # Cache the data for 24 hours (86,400 seconds)
                    cache.set(cache_key, {'country': country, 'city': city}, timeout=86400)
            except Exception:
                # Handle API errors silently, leave country and city as None
                pass

        # Create and save RequestLog instance
        try:
            RequestLog.objects.create(
                ip_address=ip_address,
                timestamp=timestamp,
                path=path,
                country=country,
                city=city
            )
        except Exception:
            # Handle potential database errors silently to avoid disrupting request processing
            pass

        # Process the request and return the response
        response = self.get_response(request)
        return response