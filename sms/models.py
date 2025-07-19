from django.db import models
from django.contrib.auth.models import User, AbstractUser

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    credits = models.PositiveIntegerField()
    description = models.TextField()
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    credits = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Student'),
        (2, 'Teacher'),
        (3, 'Admin'),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'sms_user'

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    joining_date = models.DateField()
    
    def __str__(self):
        return self.user.get_full_name()

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_number = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    admission_date = models.DateField()
    
    def __str__(self):
        return f"{self.enrollment_number} - {self.user.get_full_name()}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('student', 'subject')
    
    def __str__(self):
        return f"{self.student} - {self.subject}"

class Grade(models.Model):
    GRADE_CHOICES = [
        ('A', 'Excellent'),
        ('B', 'Good'),
        ('C', 'Average'),
        ('D', 'Below Average'),
        ('F', 'Fail'),
    ]
    
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES)
    remarks = models.TextField(blank=True)
    date_assigned = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.enrollment} - {self.grade}"