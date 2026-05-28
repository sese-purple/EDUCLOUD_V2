from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ProfileView, StudentDashboardView, InstitutionViewSet, UserViewSet, CourseViewSet, EnrollmentViewSet, GradeViewSet,
                    ClassSessionViewSet, AttendanceRecordViewSet,
                    ProjectGroupViewSet, TaskViewSet, QuestionViewSet, QuizViewSet, QuizAttemptViewSet,
                    AttemptAnswerViewSet, AssignmentViewSet, SubmissionViewSet,
                    DashboardStatsView, MyInstitutionSettingsView,
                    BulkUserImportView, DownloadTemplateView,
                    MaterialViewSet, InstructorDashboardView)

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
router.register(r'questions', QuestionViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'attempts', QuizAttemptViewSet)
router.register(r'answers', AttemptAnswerViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'submissions', SubmissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('my-institution/', MyInstitutionSettingsView.as_view(), name='my-institution'),
    path('bulk-import/', BulkUserImportView.as_view(), name='bulk-import'),
    path('download-template/', DownloadTemplateView.as_view(), name='download-template'),
    path('instructor-dashboard/', InstructorDashboardView.as_view(), name='instructor-dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('student-dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
]
