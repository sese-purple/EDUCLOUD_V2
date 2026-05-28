from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (InstitutionViewSet, UserViewSet, CourseViewSet, EnrollmentViewSet, GradeViewSet,
                    ClassSessionViewSet, AttendanceRecordViewSet,
                    ProjectGroupViewSet, TaskViewSet, QuizViewSet, QuizAttemptViewSet, AttemptAnswerViewSet,
                    DashboardStatsView)

router = DefaultRouter()
router.register(r'institutions', InstitutionViewSet)
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'sessions', ClassSessionViewSet)
router.register(r'attendance', AttendanceRecordViewSet)
router.register(r'groups', ProjectGroupViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'attempts', QuizAttemptViewSet)
router.register(r'answers', AttemptAnswerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
