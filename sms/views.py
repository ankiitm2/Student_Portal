from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import User, Course, Student, Teacher, Subject, Department, Enrollment
from .forms import (
    UserRegisterForm, 
    StudentRegisterForm, 
    TeacherRegisterForm,
    StudentEditForm,
    TeacherEditForm,
    CourseForm,
    SubjectForm
)

# Authentication Views
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'sms/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def register(request):
    # Initialize all forms first
    user_form = UserRegisterForm(request.POST or None)
    student_form = StudentRegisterForm(request.POST or None)
    teacher_form = TeacherRegisterForm(request.POST or None)
    
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = int(user_type)
            user.save()

            success = False
            if user.user_type == 1:  # Student
                if student_form.is_valid():
                    student = student_form.save(commit=False)
                    student.user = user
                    student.save()
                    success = True
                    messages.success(request, 'Student account created successfully!')
                else:
                    for field, errors in student_form.errors.items():
                        for error in errors:
                            messages.error(request, f"Student {field}: {error}")
            elif user.user_type == 2:  # Teacher
                if teacher_form.is_valid():
                    teacher = teacher_form.save(commit=False)
                    teacher.user = user
                    teacher.save()
                    success = True
                    messages.success(request, 'Teacher account created successfully!')
                else:
                    for field, errors in teacher_form.errors.items():
                        for error in errors:
                            messages.error(request, f"Teacher {field}: {error}")

            if success:
                login(request, user)
                return redirect('dashboard')
            else:
                user.delete()  # Rollback user creation if profile creation failed

    # Always pass all three forms to the template
    return render(request, 'sms/register.html', {
        'user_form': user_form,
        'student_form': student_form,
        'teacher_form': teacher_form,
        'departments': Department.objects.all()
    })

# Dashboard Views
@login_required
def dashboard(request):
    if not hasattr(request.user, 'user_type'):
        return redirect('login')
    
    context = {
        'user_type': request.user.user_type,
        'total_courses': Course.objects.count(),
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_subjects': Subject.objects.count(),
    }
    
    if request.user.user_type == 1:  # Student
        try:
            student = Student.objects.get(user=request.user)
            context.update({
                'student': student,
                'enrollments': Enrollment.objects.filter(student=student, is_active=True),
                'subjects': Subject.objects.filter(course=student.course),
            })
            return render(request, 'sms/dashboards/student.html', context)
        except Student.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect('login')
    
    elif request.user.user_type == 2:  # Teacher
        try:
            teacher = Teacher.objects.get(user=request.user)
            context.update({
                'teacher': teacher,
                'courses': Course.objects.filter(department=teacher.department),
                'students': Student.objects.filter(course__department=teacher.department),
                'subjects': Subject.objects.filter(course__department=teacher.department),
            })
            return render(request, 'sms/dashboards/teacher.html', context)
        except Teacher.DoesNotExist:
            messages.error(request, "Teacher profile not found.")
            return redirect('login')
    
    return redirect('admin:index')

@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found")
        return redirect('login')
    
    enrollments = Enrollment.objects.filter(student=student, is_active=True)
    context = {
        'student': student,
        'enrollments': enrollments,
        'subjects': Subject.objects.filter(course=student.course),
    }
    return render(request, 'sms/dashboards/student.html', context)

@login_required
def teacher_dashboard(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    courses = Course.objects.filter(department=teacher.department)
    students = Student.objects.filter(course__department=teacher.department)
    
    context = {
        'teacher': teacher,
        'courses': courses,
        'students': students,
        'subjects': Subject.objects.filter(course__department=teacher.department),
    }
    return render(request, 'sms/dashboards/teacher.html', context)

# Student Views
@login_required
@permission_required('sms.view_student', raise_exception=True)
def student_list(request):
    students = Student.objects.select_related('user', 'department', 'course').all()
    return render(request, 'sms/students/list.html', {'students': students})

@login_required
@permission_required('sms.add_student', raise_exception=True)
def student_register(request):
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, 'Student registered successfully!')
            return redirect('student_list')
    else:
        form = StudentRegisterForm()
    
    return render(request, 'sms/students/register.html', {
        'form': form,
        'departments': Department.objects.all()
    })

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'sms/students/detail.html', {'student': student})

@login_required
@permission_required('sms.change_student', raise_exception=True)
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentEditForm(instance=student)
    
    return render(request, 'sms/students/edit.html', {'form': form})

@login_required
@permission_required('sms.delete_student', raise_exception=True)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.user.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('student_list')
    return render(request, 'sms/students/delete.html', {'student': student})

# Teacher Views
@login_required
@permission_required('sms.view_teacher', raise_exception=True)
def teacher_list(request):
    teachers = Teacher.objects.select_related('user', 'department').all()
    return render(request, 'sms/teachers/list.html', {'teachers': teachers})

@login_required
@permission_required('sms.add_teacher', raise_exception=True)
def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegisterForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, 'Teacher registered successfully!')
            return redirect('teacher_list')
    else:
        form = TeacherRegisterForm()
    
    return render(request, 'sms/teachers/register.html', {
        'form': form,
        'departments': Department.objects.all()
    })

@login_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, 'sms/teachers/detail.html', {'teacher': teacher})

@login_required
@permission_required('sms.change_teacher', raise_exception=True)
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherEditForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher updated successfully!')
            return redirect('teacher_detail', pk=teacher.pk)
    else:
        form = TeacherEditForm(instance=teacher)
    
    return render(request, 'sms/teachers/edit.html', {'form': form})

# Course/Subject Views
@login_required
def course_list(request):
    courses = Course.objects.select_related('department').all()
    return render(request, 'sms/courses/list.html', {'courses': courses})

@login_required
@permission_required('sms.add_course', raise_exception=True)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully!')
            return redirect('course_list')
    else:
        form = CourseForm()
    
    return render(request, 'sms/courses/create.html', {'form': form})

@login_required
def subject_list(request):
    subjects = Subject.objects.select_related('course').all()
    return render(request, 'sms/subjects/list.html', {'subjects': subjects})

@login_required
@permission_required('sms.add_subject', raise_exception=True)
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully!')
            return redirect('subject_list')
    else:
        form = SubjectForm()
    
    return render(request, 'sms/subjects/create.html', {'form': form})