import json
import hashlib
from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import ContactMessage, SiteSettings, SiteVisitor, SiteUpdate, LoginAttempt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')


def _track_visitor(request):
    """Log one row into SiteVisitor. Also auto-deletes visits older than 90 days."""
    try:
        ip = _get_client_ip(request)
        SiteVisitor.objects.create(
            ip_address=ip,
            page=request.path,
            referrer=request.META.get('HTTP_REFERER', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        # cleanup old records – keeps the DB lean
        cutoff = timezone.now() - timedelta(days=90)
        SiteVisitor.objects.filter(visited_at__lt=cutoff).delete()
    except Exception as e:
        # Don't let tracking errors break the site
        print(f"Visitor tracking error: {e}")
        pass


# ---------------------------------------------------------------------------
# Brute-force protection helpers
# ---------------------------------------------------------------------------
# Rules: 5 failed attempts from one IP within 15 minutes = locked for 15 min.

BRUTE_MAX_ATTEMPTS = 5
BRUTE_WINDOW_MINUTES = 15


def _is_ip_locked(ip):
    """Check if this IP has too many recent failed logins."""
    try:
        window_start = timezone.now() - timedelta(minutes=BRUTE_WINDOW_MINUTES)
        fails = LoginAttempt.objects.filter(
            ip_address=ip,
            attempted_at__gte=window_start,
        ).count()
        return fails >= BRUTE_MAX_ATTEMPTS
    except Exception:
        return False


def _record_failed_login(ip):
    """Save one failed attempt row."""
    try:
        LoginAttempt.objects.create(ip_address=ip)
    except Exception:
        pass


def _minutes_until_unlock(ip):
    """Return how many minutes remain on the lockout, rounded up."""
    try:
        window_start = timezone.now() - timedelta(minutes=BRUTE_WINDOW_MINUTES)
        oldest = (
            LoginAttempt.objects
            .filter(ip_address=ip, attempted_at__gte=window_start)
            .order_by('attempted_at')
            .first()
        )
        if not oldest:
            return 0
        unlock_at = oldest.attempted_at + timedelta(minutes=BRUTE_WINDOW_MINUTES)
        remaining = (unlock_at - timezone.now()).total_seconds()
        return max(0, int(remaining // 60) + 1)
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Rate-limit helper for contact form
# ---------------------------------------------------------------------------
# Rules: max 3 submissions from one IP per 10 minutes.

CONTACT_MAX_PER_WINDOW = 3
CONTACT_WINDOW_MINUTES = 10


def _is_contact_rate_limited(ip):
    """True when this IP has submitted too many messages recently."""
    try:
        window_start = timezone.now() - timedelta(minutes=CONTACT_WINDOW_MINUTES)
        count = ContactMessage.objects.filter(
            ip_address=ip,
            created_at__gte=window_start,
        ).count()
        return count >= CONTACT_MAX_PER_WINDOW
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Public portfolio pages
# ---------------------------------------------------------------------------

def portfolio_index(request):
    _track_visitor(request)
    try:
        site = SiteSettings.load()
    except Exception as e:
        print(f"SiteSettings error: {e}")
        site = None
    return render(request, 'portfolio/index.html', {'site': site})


def project_detail(request, slug):
    _track_visitor(request)
    try:
        site = SiteSettings.load()
    except Exception as e:
        print(f"SiteSettings error: {e}")
        site = None
    
    template_map = {
        'inventory-system': 'portfolio/project-inventory-system.html',
        'joint-force':       'portfolio/project-joint-force.html',
        'example':           'portfolio/project-example.html',
    }
    template = template_map.get(slug)
    if template is None:
        from django.http import Http404
        raise Http404("Project not found.")
    return render(request, template, {'site': site})


@csrf_protect
@require_POST
def contact_api(request):
    """
    AJAX endpoint: POST JSON -> validate -> save -> email -> return JSON.
    Protected by: CSRF token, honeypot field, rate limiting per IP.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

    # --- HONEYPOT: if this hidden field has any value, it's a bot ---
    if body.get('website', '').strip():
        # silently pretend it worked – bots don't know they failed
        return JsonResponse({'success': True, 'message': 'Message sent successfully!'})

    name    = body.get('name', '').strip()
    email   = body.get('email', '').strip()
    subject = body.get('subject', '').strip()
    message = body.get('message', '').strip()

    if not all([name, email, subject, message]):
        return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

    if len(subject) > 300 or len(name) > 200 or len(message) > 5000:
        return JsonResponse({'success': False, 'error': 'Input too long.'}, status=400)

    # basic email format sanity check
    if '@' not in email or '.' not in email.split('@')[-1]:
        return JsonResponse({'success': False, 'error': 'Invalid email.'}, status=400)

    ip = _get_client_ip(request)

    # --- RATE LIMIT ---
    if _is_contact_rate_limited(ip):
        return JsonResponse(
            {'success': False, 'error': 'Too many messages. Please wait a few minutes.'},
            status=429,
        )

    # 1. Save to database
    try:
        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message, ip_address=ip
        )
    except Exception as e:
        print(f"Database error: {e}")
        return JsonResponse({'success': False, 'error': 'Database error.'}, status=500)

    # 2. Mark matching SiteVisitor rows
    try:
        SiteVisitor.objects.filter(ip_address=ip).update(sent_contact=True)
    except Exception:
        pass

    # 3. Send email to your inbox
    owner_email = getattr(settings, 'ADMIN_EMAIL', settings.EMAIL_HOST_USER)

    try:
        send_mail(
            subject=f"[Portfolio] {subject}",
            message=(
                f"New contact message from your portfolio site.\n\n"
                f"Name:    {name}\n"
                f"Email:   {email}\n"
                f"Subject: {subject}\n\n"
                f"--- Message ---\n{message}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner_email],
            fail_silently=False,
        )
    except (BadHeaderError, Exception):
        pass  # saved to DB anyway

    return JsonResponse({'success': True, 'message': 'Message sent successfully!'})


# ---------------------------------------------------------------------------
# Custom admin panel – session-based auth
# ---------------------------------------------------------------------------

ADMIN_SESSION_KEY = '_portfolio_admin_auth'


def _make_token():
    raw = settings.SECRET_KEY + settings.ADMIN_PANEL_PASSWORD
    return hashlib.sha256(raw.encode()).hexdigest()


def _is_admin(request):
    expected = _make_token()
    return request.session.get(ADMIN_SESSION_KEY) == expected


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not _is_admin(request):
            return redirect('portfolio:admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


# --- login (with brute-force protection) ---

def admin_login(request):
    ip = _get_client_ip(request)
    error = None
    locked = False
    minutes_left = 0

    # check lockout BEFORE doing anything
    if _is_ip_locked(ip):
        locked = True
        minutes_left = _minutes_until_unlock(ip)
        return render(request, 'portfolio/admin_login.html', {
            'locked': True,
            'minutes_left': minutes_left,
        })

    if request.method == 'POST':
        password = request.POST.get('password', '')
        remember = request.POST.get('remember') == 'on'

        if password == settings.ADMIN_PANEL_PASSWORD:
            # correct – log in, clear old failed attempts for this IP
            request.session[ADMIN_SESSION_KEY] = _make_token()
            if remember:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
            else:
                request.session.set_expiry(3600)  # 1 hour
            try:
                LoginAttempt.objects.filter(ip_address=ip).delete()
            except Exception:
                pass
            return redirect('portfolio:admin_dashboard')
        else:
            # wrong – record it
            _record_failed_login(ip)
            # check if we just hit the limit
            if _is_ip_locked(ip):
                locked = True
                minutes_left = _minutes_until_unlock(ip)
            else:
                try:
                    window_start = timezone.now() - timedelta(minutes=BRUTE_WINDOW_MINUTES)
                    used = LoginAttempt.objects.filter(
                        ip_address=ip,
                        attempted_at__gte=window_start,
                    ).count()
                    remaining = BRUTE_MAX_ATTEMPTS - used
                    error = f'Invalid password. {remaining} attempt{"s" if remaining != 1 else ""} left.'
                except Exception:
                    error = 'Invalid password.'

    return render(request, 'portfolio/admin_login.html', {
        'error': error,
        'locked': locked,
        'minutes_left': minutes_left,
    })


def admin_logout(request):
    request.session.flush()
    return redirect('portfolio:admin_login')


# --- dashboard ---

@admin_required
def admin_dashboard(request):
    try:
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total_visits   = SiteVisitor.objects.count()
        today_visits   = SiteVisitor.objects.filter(visited_at__gte=today_start).count()
        total_messages = ContactMessage.objects.count()
        unread         = ContactMessage.objects.filter(is_read=False).count()

        chart_labels = []
        chart_values = []
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end   = day_start + timedelta(days=1)
            count = SiteVisitor.objects.filter(visited_at__gte=day_start, visited_at__lt=day_end).count()
            chart_labels.append(day.strftime('%a'))
            chart_values.append(count)

        recent_messages = ContactMessage.objects.order_by('-created_at')[:5]

        ctx = {
            'total_visits': total_visits,
            'today_visits': today_visits,
            'total_messages': total_messages,
            'unread': unread,
            'chart_labels': json.dumps(chart_labels),
            'chart_values': json.dumps(chart_values),
            'recent_messages': recent_messages,
        }
    except Exception as e:
        print(f"Dashboard error: {e}")
        ctx = {
            'total_visits': 0,
            'today_visits': 0,
            'total_messages': 0,
            'unread': 0,
            'chart_labels': json.dumps([]),
            'chart_values': json.dumps([]),
            'recent_messages': [],
        }
    return render(request, 'portfolio/admin_dashboard.html', ctx)


# --- visitors ---

@admin_required
def admin_visitors(request):
    try:
        visitors = SiteVisitor.objects.order_by('-visited_at')[:200]
    except Exception:
        visitors = []
    return render(request, 'portfolio/admin_visitors.html', {'visitors': visitors})


# --- messages ---

@admin_required
def admin_messages(request):
    try:
        messages = ContactMessage.objects.order_by('-created_at')
        messages.update(is_read=True)
    except Exception:
        messages = []
    return render(request, 'portfolio/admin_messages.html', {'messages': messages})


# --- updates / versions ---

@admin_required
def admin_updates(request):
    try:
        updates = SiteUpdate.objects.order_by('-deployed_at')
    except Exception:
        updates = []
    return render(request, 'portfolio/admin_updates.html', {'updates': updates})