from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import CalendarFeedToken


@login_required
def settings_view(request):
    feed_token, _ = CalendarFeedToken.objects.get_or_create(user=request.user)
    feed_url = request.build_absolute_uri(reverse('planner:ics_feed', args=[feed_token.token]))

    return render(request, "account/settings.html", {'feed_url': feed_url})


@login_required
@require_POST
def regenerate_feed_token(request):
    CalendarFeedToken.objects.filter(user=request.user).delete()
    CalendarFeedToken.objects.create(user=request.user)
    return redirect('account:settings')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:overview')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            user.last_login = timezone.now()
            user.save()
            login(request, user)
            next_url = request.GET.get("next")
            if not next_url:
                return redirect('core:overview')
            return redirect(next_url)
        else:
            return render(request, "account/login.html", {'error': 'Invalid username or password'})
    else:
        return render(request, "account/login.html")


def logout_view(request):
    logout(request)
    return redirect('account:login')
