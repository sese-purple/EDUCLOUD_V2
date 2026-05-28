from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserViewSet, CourseViewSet, EnrollmentViewSet, GradeViewSet,
                    ClassSessionViewSet, AttendanceRecordViewSet,
                    ProjectGroupViewSet, TaskViewSet, QuizViewSet,QuizAttemptViewSet, AttemptAnswerViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'grades', GradeViewSet)                     # The Mark Sheet API
router.register(r'sessions', ClassSessionViewSet)            # The GPS/QR API
router.register(r'attendance', AttendanceRecordViewSet)
router.register(r'groups', ProjectGroupViewSet)              # The Agile Workspace API
router.register(r'tasks', TaskViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'attempts', QuizAttemptViewSet)
router.register(r'answers', AttemptAnswerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]