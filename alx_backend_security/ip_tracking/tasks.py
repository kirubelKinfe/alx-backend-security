from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from ip_tracking.models import RequestLog, SuspiciousIP

@shared_task
def detect_anomalies():
    # Calculate time range for the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    # Define sensitive paths
    sensitive_paths = ['/admin', '/admin/', '/login', '/login/']
    
    # Query RequestLog for high request volume (>100 requests/hour)
    high_request_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(request_count=Count('ip_address'))
        .filter(request_count__gt=100)
    )
    
    # Query RequestLog for IPs accessing sensitive paths
    sensitive_path_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago, path__in=sensitive_paths)
        .values('ip_address')
        .distinct()
    )
    
    # Combine IPs to flag
    flagged_ips = set()
    for entry in high_request_ips:
        flagged_ips.add((entry['ip_address'], f"Exceeded 100 requests/hour: {entry['request_count']} requests"))
    
    for entry in sensitive_path_ips:
        flagged_ips.add((entry['ip_address'], f"Accessed sensitive path"))
    
    # Create SuspiciousIP entries, avoiding duplicates
    for ip_address, reason in flagged_ips:
        try:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip_address,
                defaults={'reason': reason}
            )
        except Exception:
            # Handle potential database errors silently
            pass