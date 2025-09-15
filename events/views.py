from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from .models import User, Event, Club
from .forms import ClubRegistrationForm
from datetime import datetime
from django.utils.timezone import make_aware

# ========== Public Views ==========

# def index(request):
#     """Public homepage view showing approved events."""
#     # events = Event.objects.filter(approved=True).order_by('date', 'start_time')
#     now = make_aware(datetime.now())
#     events = Event.objects.filter(approved=True, date__gte=now.date()).order_by('date', 'start_time')
#     next_event = Event.objects.filter(approved=True,date__gte=now.date()).order_by('date', 'start_time').first()
    
#     return render(request, 'index.html', {'events': events,'next_event': next_event})

from django.shortcuts import render
from django.utils.timezone import make_aware
from datetime import datetime
from itertools import zip_longest
from django.db.models import Q
from .models import Event
from .forms import ContactForm


def batch_events(iterable, n=3):
    """Group events into batches of size n"""
    args = [iter(iterable)] * n
    return list(zip_longest(*args, fillvalue=None))
def batch_items(iterable, n=6):
    from itertools import zip_longest
    args = [iter(iterable)] * n
    return list(zip_longest(*args, fillvalue=None))
def index(request):
    now = make_aware(datetime.now())

    # Only fetch approved events that are upcoming (either future date or today with future start_time)
    events = Event.objects.filter(
        approved=True).filter(Q(date__gt=now.date()) | Q(date=now.date(), start_time__gte=now.time())).order_by('date', 'start_time')

    event_batches = batch_events(events, 3)
    next_event = events.first() if events else None
    previous_qs = Event.objects.filter(
        approved=True,
        date__lt=now.date()
    ).order_by('-date', '-start_time')
    previous_batches = batch_events(previous_qs, 3)
    print(previous_batches)
    clubs = Club.objects.all()
    club_batches = batch_items(clubs, 6)

    contact_form = ContactForm()

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            # Optionally, add a success message or redirect
            return redirect('index')  

    return render(request, 'index.html', {
        'event_batches': event_batches,
        'next_event': next_event,
        'events': events,
        'previous_events': previous_batches,
        'club_batches': club_batches
    })


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import ContactMessage

@staff_member_required  # only admin/staff can view messages
def view_contact_messages(request):
    messages = ContactMessage.objects.order_by('-submitted_at')
    return render(request, 'events/usermessages.html', {'messages': messages})


# ========== Authentication Views ==========

def club_register(request):
    if request.method == 'POST':
        form = ClubRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = False
            user.is_staff = True
            user.is_active = False
            user.role = 'club'
            user.save()
            
            Club.objects.create(
                user=user,
                name=user.username, 
                description="",
                contact_email=user.email
            )

            return HttpResponse("""
                <script>
                    alert('Successfully Registered! Wait for Admin Approval');
                    window.location.href = '/';
                </script>
            """)
    else:
        form = ClubRegistrationForm()
    return render(request, 'events/club_register.html', {'form': form})



def custom_login(request):
    """Custom login view with role-based redirects."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.is_staff and user.is_active:
                return redirect('club_dashboard')
            else:
                return HttpResponse("""
                    <script>
                        alert('Your account is not yet approved by the admin.');
                        window.location.href = '/login/';
                    </script>
                """)
    else:
        form = AuthenticationForm()
    return render(request, 'events/login.html', {'form': form})


def custom_logout(request):
    """Logout and redirect to login."""
    logout(request)
    return redirect('login')


# ========== Admin Views ==========

def admin_dashboard(request):
    events_with_club = Event.objects.select_related('club').all()
    print(events_with_club)
    return render(request, 'events/admin_dashboard.html', {
        'events': events_with_club
    })




from django.shortcuts import render
from .models import Club, User

def admin_club_manage(request):
    all_clubs = User.objects.filter(is_staff=True, is_superuser=False)
    return render(request, 'events/admin_club_approval.html', {
        'all_clubs': all_clubs
    })



from django.core.paginator import Paginator

def admin_event_manage(request):
    all_pending = Event.objects.filter(approved=False).order_by('-date')
    paginator = Paginator(all_pending, 10)  # 10 events per page
    page_number = request.GET.get('page')
    events_pending_approval = paginator.get_page(page_number)
    return render(request, 'events/admin_events.html', {
        'events_pending_approval': events_pending_approval
    })



def approve_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.approved = True
    event.save()
    return redirect('admin_event_manage')  # Instead of 'admin_dashboard'



def reject_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('admin_events')  # Instead of 'admin_dashboard'



def approve_club(request, club_id):
    """Approve a registered club account."""
    club = get_object_or_404(User, id=club_id)
    club.is_active = True
    club.save()
    return redirect('admin_dashboard')

def suspend_club(request, club_id):
    """Approve a registered club account."""
    club = get_object_or_404(User, id=club_id)
    club.is_active = False
    club.save()
    return redirect('admin_dashboard')


# ========== Club Views ==========

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
@login_required
def club_dashboard(request):
    user = request.user
    try:
        club = Club.objects.get(user=user)
        events = Event.objects.filter(club=club).order_by('-date')
    except Club.DoesNotExist:
        # return HttpResponse("No club profile associated with your account.")
        return HttpResponse("""
                    <script>
                        alert('No club profile associated with your account.');
                        window.location.href = '/login/';
                    </script>
                """)

    return render(request, 'events/club_home.html', {
        'events': events,
        'club': club
    })



def manage_event(request):
    user = request.user
    try:
        club = Club.objects.get(user=user)
        events = Event.objects.filter(club=club).order_by('-date')
    except Club.DoesNotExist:
        # return HttpResponse("No club profile associated with your account.")
        return HttpResponse("""
                    <script>
                        alert('No club profile associated with your account.');
                        window.location.href = '/login/';
                    </script>
                """)


    return render(request, 'events/manage_events.html', {
        'events': events,
        'club': club
    })


from .forms import EventForm
from django.contrib.auth.decorators import login_required

from .models import Club  # Make sure this is imported

@login_required
def add_event(request):
    user = request.user
    try:
        club = Club.objects.get(user=user)  # ✅ Get Club, not User
    except Club.DoesNotExist:
        return HttpResponse("No club associated with your account.")
    if request.method == 'POST':
        print('/////')
        # form = EventForm(request.POST)
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            event = form.save(commit=False)
            event.club = club  # ✅ Assign the Club instance
            event.approved = False  # Must be approved by admin
            event.save()
            print('?????/')
            return HttpResponse("""
                <script>
                    alert('Created Successfully...Wait for Approval!');
                    window.location.href = '/club/add_event/';
                </script>
            """)

    else:
        form = EventForm()

    return render(request, 'events/add_event.html', {'form': form})





from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from .models import Event, Club
from .forms import EventForm
from django.contrib.auth.decorators import login_required

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Ensure the logged-in user is the owner of the event
    if event.club.user != request.user:
        return HttpResponseForbidden("You are not allowed to edit this event.")

    if request.method == 'POST':
        # form = EventForm(request.POST, instance=event)
        form = EventForm(request.POST, request.FILES, instance=event)

        if form.is_valid():
            edited_event = form.save(commit=False)
            edited_event.approved = False  # Re-approval required after editing
            edited_event.save()
            return redirect('club_dashboard')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})



@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Ensure the logged-in user is the owner of the event
    if event.club.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this event.")

    event.delete()
    return redirect('club_dashboard')




# views.py
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Feedback
from .forms import FeedbackForm

def feedbacks_view(request, id):
    event = get_object_or_404(Event, id=id)
    feedbacks = Feedback.objects.filter(event=event)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Save the new feedback for the event
            feedback = form.save(commit=False)
            feedback.event = event
            feedback.save()
            return redirect('feedbacks', id=event.id)  # Redirect to the same page to show updated feedbacks
    else:
        form = FeedbackForm()

    return render(request, 'events/feedbacks.html', {'event': event, 'form': form, 'feedbacks': feedbacks})





from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Feedback
from django.shortcuts import render, get_object_or_404
from .models import Feedback, Club
from django.utils import timezone
from collections import defaultdict

def club_view_feedbacks(request):
    club = get_object_or_404(Club, user=request.user)
    past_events = Event.objects.filter(club=club, date__lt=timezone.now()).order_by('-date')
    feedbacks = Feedback.objects.select_related('event').filter(event__in=past_events)

    events_with_feedback = defaultdict(list)
    for feedback in feedbacks:
        events_with_feedback[feedback.event].append(feedback)

    # Convert to template-friendly list
    events_feedback_list = [
        {'event': event, 'feedback_list': feedback_list}
        for event, feedback_list in events_with_feedback.items()
    ]
    print(events_feedback_list)
    return render(request, 'events/clubfeedbacks.html', {
        'events_feedback_list': events_feedback_list
    })


