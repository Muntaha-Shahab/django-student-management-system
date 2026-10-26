from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.contrib import messages
from .models import Student

# ------------------- SIGNUP -------------------
def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Check if username/email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('/signup/')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('/signup/')

        # Create inactive user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_active = False
        user.save()

        # -------- ACTIVATION LINK --------
        activation_link = (
            request.scheme + "://" +
            request.META['HTTP_HOST'] +
            "/activate/" + str(user.id) + "/"
        )

        # -------- EMAIL MESSAGE --------
        email_message = EmailMessage(
            "Activate Your Account",
            f"""Hi {user.username},

Please click the link below to activate your account:

{activation_link}

Thank you,
Student Management System
""",
            "S2023065020@umt.edu.pk",
            [email],
        )

        # -------- SEND ACTIVATION EMAIL --------
        sent_count = email_message.send(fail_silently=False)

        if sent_count == 1:
            messages.success(
                request,
                "Account created! Please check your email to activate."
            )
        else:
            messages.error(
                request,
                "Your account was created, but the verification email could not be sent."
            )

        return redirect('/')

    return render(request, 'signup.html')



# ------------------- ACTIVATE ACCOUNT -------------------
def activate_account(request, uid):
    try:
        user = User.objects.get(id=uid)
        user.is_active = True
        user.save()
        messages.success(request, "Account activated successfully!")
    except User.DoesNotExist:
        messages.error(request, "Invalid activation link")
    return redirect('/')


# ------------------- LOGIN -------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('/dashboard/')
            else:
                messages.error(request, "Account is not activated. Check your email.")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')


# ------------------- LOGOUT -------------------
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('/')


# ------------------- DASHBOARD -------------------
@login_required
def dashboard(request):
    search = request.GET.get('search')
    students = Student.objects.filter(name__icontains=search) if search else Student.objects.all()
    return render(request, 'dashboard.html', {
        'students': students,
        'total': students.count()
    })


# ------------------- ADD STUDENT -------------------
@login_required
def add_student(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        age = request.POST['age']
        course = request.POST['course']

        # Validate required fields
        if not name or not email or not age or not course:
            messages.error(request, "All fields are required")
            return redirect('/dashboard/')

        Student.objects.create(
            name=name,
            email=email,
            age=age,
            course=course
        )
        messages.success(request, "Student added successfully")
        return redirect('/dashboard/')


# ------------------- EDIT STUDENT -------------------
@login_required
def edit_student(request, id):
    student = Student.objects.get(id=id)
    if request.method == 'POST':
        student.name = request.POST['name']
        student.email = request.POST['email']
        student.age = request.POST['age']
        student.course = request.POST['course']
        student.save()
        messages.success(request, "Student updated successfully")
        return redirect('/dashboard/')

    # Render dashboard with edit fields pre-filled
    students = Student.objects.all()
    return render(request, 'dashboard.html', {
        'students': students,
        'total': students.count(),
        'edit_student': student
    })


# ------------------- DELETE STUDENT -------------------
@login_required
def delete_student(request, id):
    student = Student.objects.get(id=id)
    student.delete()
    messages.success(request, "Student deleted successfully")
    return redirect('/dashboard/')
