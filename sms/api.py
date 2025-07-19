from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Course

@require_GET
def get_courses(request):
    department_id = request.GET.get('department_id')
    if department_id:
        courses = Course.objects.filter(department_id=department_id).values('id', 'name')
        return JsonResponse({'courses': list(courses)})
    return JsonResponse({'courses': []})