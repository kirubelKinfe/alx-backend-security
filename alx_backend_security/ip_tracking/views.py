from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_ratelimit.decorators import ratelimit

def login_view(request):
    # Apply rate limiting: 10 requests/min for authenticated, 5 requests/min for anonymous
    @ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True)
    @ratelimit(key='ip', rate='5/m', method='POST', block=True, group='anonymous')
    def process_request(request):
        if request.method == 'POST':
            # Handle login form submission
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to a home page or dashboard
            else:
                # Return error message for invalid credentials
                return render(request, 'ip_tracking/login.html', {
                    'error': 'Invalid username or password'
                })
        else:
            # Render login form for GET requests
            return render(request, 'ip_tracking/login.html')

    try:
        return process_request(request)
    except ratelimit.Ratelimited:
        return HttpResponse('Request limit exceeded.', status=429)