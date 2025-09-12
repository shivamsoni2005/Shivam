from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Student, Admin, Event
from django.contrib.auth.hashers import make_password, check_password
from .forms import EventForm
import jwt
import datetime

SECRET_KEY = "iamsecretkey"


# -- HTML pages --
def signup(request):
    return render(request, 'accounts/signup.html')


def login_view(request):
    """
    Session-based login using your Student and Admin models (not django.contrib.auth).
    Expects form fields: username, password, role
    """
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        role = (request.POST.get("role") or "").strip().lower()

        # map common variants -> student/admin
        if role in ("user", "student", "stu"):
            role = "student"
        if role in ("admin", "administrator"):
            role = "admin"

        if not username or not password or role not in ("student", "admin"):
            return render(request, "accounts/login.html", {"error": "Please provide username, password and role."})

        if role == "student":
            try:
                # case-insensitive lookup
                student = Student.objects.get(username__iexact=username)
            except Student.DoesNotExist:
                return render(request, "accounts/login.html", {"error": "Student not found."})

            if check_password(password, student.password):
                # login success -> store session
                request.session["user_id"] = student.id
                request.session["role"] = "student"
                # optional: set session expiry in seconds (e.g., 1 day)
                # request.session.set_expiry(86400)
                return redirect("dashboard2")
            else:
                return render(request, "accounts/login.html", {"error": "Invalid password."})

        elif role == "admin":
            try:
                admin = Admin.objects.get(username__iexact=username)
            except Admin.DoesNotExist:
                return render(request, "accounts/login.html", {"error": "Admin not found."})

            if check_password(password, admin.password):
                request.session["user_id"] = admin.id
                request.session["role"] = "admin"
                return redirect("dashboard1")
            else:
                return render(request, "accounts/login.html", {"error": "Invalid password."})

    # GET (or any other) -> show login page
    return render(request, "accounts/login.html")


# ---------------- STUDENT REGISTER ----------------
@csrf_exempt
def register_student(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Wrong method"})

    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return JsonResponse({"error": "All Fields are Required"})

        if Student.objects.filter(username=username).exists() or Student.objects.filter(email=email).exists():
            return JsonResponse({"error": "User Already Exist"})

        student = Student(username=username, email=email, password=make_password(password))
        student.save()

        return JsonResponse({"message": "User created successfully", "status": True})
    except Exception as e:
        return JsonResponse({"error": str(e)})


# ---------------- ADMIN REGISTER ----------------
@csrf_exempt
def register_admin(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Wrong method"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return JsonResponse({"error": "All fields are required"})

        if Admin.objects.filter(username=username).exists() or Admin.objects.filter(email=email).exists():
            return JsonResponse({"error": "User Already Exist"})

        admin = Admin(username=username, email=email, password=make_password(password))
        admin.save()

        return JsonResponse({"message": "Admin created successfully", "status": True})
    except Exception as e:
        return JsonResponse({"error": str(e)})


# ---------------- JWT LOGIN (if you need API tokens) ----------------
@csrf_exempt
def login_student(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Wrong method"})

    data = json.loads(request.body)
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    try:
        student = Student.objects.get(username__iexact=username)
        if check_password(password, student.password):
            payload = {
                "id": student.id,
                "username": student.username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return JsonResponse({"token": token, "status": True})
        else:
            return JsonResponse({"error": "Invalid password"})
    except Student.DoesNotExist:
        return JsonResponse({"error": "User not found"})


@csrf_exempt
def login_admin(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Wrong method"})

    data = json.loads(request.body)
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    try:
        admin = Admin.objects.get(username__iexact=username)
        if check_password(password, admin.password):
            payload = {
                "id": admin.id,
                "username": admin.username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return JsonResponse({"token": token, "status": True})
        else:
            return JsonResponse({"error": "Invalid password"})
    except Admin.DoesNotExist:
        return JsonResponse({"error": "User not found"})


# ---------------- DASHBOARD ----------------
def dashboard1(request):
    # require session login
    if not request.session.get("user_id"):
        return redirect("login")

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard1")
    else:
        form = EventForm()

    events = Event.objects.all().order_by("-date")
    return render(request, "accounts/dashboard1.html", {"form": form, "events": events, "role": request.session.get("role")})

def dashboard2(request):
    # require session login
    if not request.session.get("user_id"):
        return redirect("login")

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard2")
    else:
        form = EventForm()

    events = Event.objects.all().order_by("-date")
    return render(request, "accounts/dashboard2.html", {"form": form, "events": events, "role": request.session.get("role")})


# useful: logout
def logout_view(request):
    request.session.flush()
    return redirect("login")


from django.shortcuts import render
from django.utils import timezone
from .models import Event

def upcoming_events(request):
    # Get only future events, sorted by date
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    return render(request, "dashboard.html", {"events": events})

