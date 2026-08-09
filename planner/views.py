import calendar
from icalendar import Calendar, Event as IcalEvent
from datetime import timedelta, datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
from django.utils.timezone import make_aware
from django.core.paginator import Paginator
from django.db.models import Q
from core.calendar_sources import get_all_items, get_sources, get_source_subgroups
from .models import Event, Category, Contact 




@login_required
def index_view(request):
    # 1. Determine target date and active view
    active_view = request.GET.get('view', 'month')
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.localdate()
    else:
        target_date = timezone.localdate()

    year = target_date.year
    month = target_date.month

    # 2. Calculate specific Navigation Dates based on the active view
    if active_view == 'week':
        prev_date = target_date - timedelta(weeks=1)
        next_date = target_date + timedelta(weeks=1)
    elif active_view == 'day':
        prev_date = target_date - timedelta(days=1)
        next_date = target_date + timedelta(days=1)
    else:
        active_view = 'month'
        first_day_of_month = target_date.replace(day=1)
        prev_date = first_day_of_month - timedelta(days=1)
        next_date = (first_day_of_month + timedelta(days=32)).replace(day=1)

    # 3. Generate Grids
    cal = calendar.Calendar(firstweekday=0)
    month_days = [day for week in cal.monthdatescalendar(year, month) for day in week]

    start_of_week = target_date - timedelta(days=target_date.weekday())
    week_days = [start_of_week + timedelta(days=i) for i in range(7)]

    # 4. Fetch Events
    start_date = month_days[0]
    end_date = month_days[-1]

    items = get_all_items(start_date, end_date, request.user)

    events_by_date = {day: [] for day in month_days}
    allday_by_date = {day: [] for day in month_days}
    for item in items:
        if item.date not in events_by_date:
            continue
        if item.all_day:
            allday_by_date[item.date].append(item)
        else:
            start_minutes = item.start_time.hour * 60 + item.start_time.minute
            end_minutes = item.end_time.hour * 60 + item.end_time.minute if item.end_time else start_minutes + 30

            height = max(end_minutes - start_minutes, 20)
            events_by_date[item.date].append({'item': item, 'top_px': start_minutes, 'height_px': height})

    # 5. Build Final Context
    calendar_month_grid = []
    for day in month_days:
        calendar_month_grid.append({
            'date': day,
            'is_current_month': day.month == month,
            'is_today': day == timezone.localdate(),
            'allday_events': allday_by_date.get(day, []),
            'events': events_by_date.get(day, []),
        })

    calendar_week_grid = []
    for day in week_days:
        calendar_week_grid.append({
            'date': day,
            'is_today': day == timezone.localdate(),
            'events': events_by_date.get(day, []),
            'allday_events': allday_by_date.get(day, []),
        })

    # Formatting text
    german_months = ["", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    german_weekdays_long = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

    context = {
        'active_view': active_view,
        'target_date': target_date.strftime('%Y-%m-%d'),

        'prev_date': prev_date.strftime('%Y-%m-%d'),
        'next_date': next_date.strftime('%Y-%m-%d'),

        'month_title': f"{german_months[month]} {year}",
        'week_title': f"{week_days[0].day}. {german_months[week_days[0].month][:3]} - {week_days[-1].day}. {german_months[week_days[-1].month][:3]} {year}",
        'day_title': f"{german_weekdays_long[target_date.weekday()]}, {target_date.day}. {german_months[month]} {year}",

        'calendar_month_grid': calendar_month_grid,
        'calendar_week_grid': calendar_week_grid,
        'day_events': events_by_date.get(target_date, []),
        'day_allday_events': allday_by_date.get(target_date, []),
        'target_day_is_today': target_date == timezone.localdate(),

        'categories': Category.objects.all(),
        'calendar_sources': [
            {'key': s.key, 'label': s.label, 'subgroups': get_source_subgroups(s)}
            for s in get_sources()
        ],
    }

    return render(request, "planner/index.html", context)


@login_required
def event_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        category_id = request.POST.get('category')
        description = request.POST.get('description')

        try:
            start_dt = make_aware(datetime.combine(parse_date(start_date), parse_time(start_time)))
            end_dt = make_aware(datetime.combine(parse_date(end_date), parse_time(end_time)))
            category = Category.objects.filter(id=category_id).first() if category_id else None

            Event.objects.create(
                title=title,
                start_time=start_dt,
                end_time=end_dt,
                category=category,
                description=description
            )
        except (TypeError, ValueError):
            # NOTE: handle invalid date formats or missing data here
            pass

    return redirect(request.META.get('HTTP_REFERER', 'index'))


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            event.delete()
            return redirect('planner:overview')

        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        category_id = request.POST.get('category')
        event.category = Category.objects.filter(id=category_id).first() if category_id else None

        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')

        try:
            event.start_time = make_aware(datetime.combine(parse_date(start_date), parse_time(start_time)))
            event.end_time = make_aware(datetime.combine(parse_date(end_date), parse_time(end_time)))
            event.full_clean()
            event.save()
            return redirect(f'{reverse('planner:overview')}?date={event.start_time.date()}&view=day')
        except (TypeError, ValueError):
            pass

    return render(request, 'planner/event_detail.html', {
        'event': event,
        'categories': Category.objects.all(),
    })


# TODO: Add a unique UUID token to the feed as identifer to secure access
def event_ics_feed(request):
    cal = Calendar()
    cal.add('prodid', '-//PAM//Alle Events//')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', 'Mein Planner (Alle)')

    today = timezone.localdate()
    start_date = today - timedelta(days=365)
    end_date = today + timedelta(days=730)

    items = get_all_items(start_date, end_date, request.user)

    for item in items:
        ical_event = IcalEvent()
        ical_event.add('summary', item.title)

        if item.description:
            ical_event.add('description', item.description)

        if item.all_day:
            ical_event.add('dtstart', item.date)
            ical_event.add('dtend', item.date + timedelta(days=1))
        else:
            ical_event.add('dtstart', make_aware(datetime.combine(item.date, item.start_time)))
            ical_event.add('dtend', make_aware(datetime.combine(item.date, item.end_time or item.start_time)))

        ical_event.add('dtstamp', timezone.now())
        ical_event.add('uid', f'{item.source_key}-{item.url}-{item.date.isoformat()}@ampferl.com')

        cal.add_component(ical_event)

    response = HttpResponse(cal.to_ical(), content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="alle_events.ics"'
    return response


@login_required
def contacts_view(request, contact_id:int=None):
    contacts = Contact.objects.all()

    search_query = request.GET.get('q', '').strip().lower()
    if search_query:
        contacts = contacts.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    paginator = Paginator(contacts, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    selected_contact = None
    if contact_id:
        selected_contact = Contact.objects.filter(id=contact_id).first()

    if request.GET.get('new') == 'true':
        selected_contact = None
    elif not selected_contact and page_obj.object_list:
        selected_contact = page_obj.object_list[0]

    return render(request, 'planner/contacts.html', {
        'page_obj': page_obj,
        'contact': selected_contact,
        'search_query': search_query
    })

@login_required
@require_POST
def contact_save(request, contact_id=None):
    if contact_id:
        contact = get_object_or_404(Contact, id=contact_id)

        if request.POST.get('action') == 'delete':
            contact.delete()
            return redirect('planner:contacts')
    else:
        contact = Contact()

    contact.first_name = request.POST.get('first_name', '')
    contact.last_name = request.POST.get('last_name', '')
    contact.email = request.POST.get('email', '')
    contact.phone = request.POST.get('phone', '')
    contact.address = request.POST.get('address', '')
    contact.birthday = request.POST.get('birthday', '')
    contact.notes = request.POST.get('notes', '')

    contact.save()

    return redirect('planner:contact', contact_id=contact.id)

