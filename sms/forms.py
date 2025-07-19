from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Student, Teacher, Department, Course, Subject

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 'password1', 'password2']

class StudentRegisterForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['enrollment_number', 'department', 'course', 'admission_date']
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.none()

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['course'].queryset = Course.objects.filter(department_id=department_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['course'].queryset = self.instance.department.course_set.all()

class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['enrollment_number', 'department', 'course', 'admission_date']
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.department:
            self.fields['course'].queryset = Course.objects.filter(department=self.instance.department)
        else:
            self.fields['course'].queryset = Course.objects.none()

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['course'].queryset = Course.objects.filter(department_id=department_id)
            except (ValueError, TypeError):
                pass

class TeacherRegisterForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['department', 'qualification', 'specialization', 'joining_date']
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'})
        }

class TeacherEditForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['department', 'qualification', 'specialization', 'joining_date']
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'})
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'department', 'credits', 'description']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'course', 'credits']