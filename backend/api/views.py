from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count, Q
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import (Institution, User, Course, Enrollment, Grade, ClassSession,
                     AttendanceRecord, ProjectGroup, Task, Quiz, QuizAttempt, AttemptAnswer)
from .serializers import (InstitutionSerializer, UserSerializer, CourseSerializer,
                          EnrollmentSerializer, GradeSerializer, ClassSessionSerializer,
                          AttendanceRecordSerializer, ProjectGroupSerializer, TaskSerializer,
                          QuizSerializer, QuizAttemptSerializer, AttemptAnswerSerializer)


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.all()
        if user.role != 'super_admin' and user.institution:
            qs = qs.filter(institution=user.institution)
        elif user.role != 'super_admin':
            return User.objects.none()
        search = self.request.query_params.get('search', None)
        if search:
            qs = qs.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        return qs

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Course.objects.all()
        if user.role != 'super_admin' and user.institution:
            qs = qs.filter(institution=user.institution)
        elif user.role != 'super_admin':
            return Course.objects.none()
        search = self.request.query_params.get('search', None)
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(course_code__icontains=search) |
                Q(description__icontains=search)
            )
        return qs

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class DashboardStatsView(APIView):
    def get(self, request):
        users_count = User.objects.count()
        courses_count = Course.objects.count()
        enrollments_count = Enrollment.objects.count()
        recent_courses = Course.objects.order_by('-created_at')[:5]
        recent_users = User.objects.order_by('-date_joined')[:5]
        activities = []
        for c in recent_courses:
            activities.append({
                'id': f'course-{c.id}',
                'action': f'Created course: {c.title} ({c.course_code})',
                'user': c.instructor.username if c.instructor else 'System',
                'time': c.created_at.isoformat() if c.created_at else '',
            })
        for u in recent_users:
            activities.append({
                'id': f'user-{u.id}',
                'action': f'Registered user: {u.username} ({u.get_role_display()})',
                'user': 'System',
                'time': u.date_joined.isoformat() if u.date_joined else '',
            })
        activities.sort(key=lambda x: x['time'], reverse=True)
        return Response({
            'total_users': users_count,
            'total_courses': courses_count,
            'total_enrollments': enrollments_count,
            'recent_activities': activities[:10],
        })


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Enrollment.objects.all()
        if user.institution:
            return Enrollment.objects.filter(student__institution=user.institution)
        return Enrollment.objects.none()


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Grade.objects.all()
        if user.institution:
            return Grade.objects.filter(student__institution=user.institution)
        return Grade.objects.none()


class ClassSessionViewSet(viewsets.ModelViewSet):
    queryset = ClassSession.objects.all()
    serializer_class = ClassSessionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return ClassSession.objects.all()
        if user.institution:
            return ClassSession.objects.filter(course__institution=user.institution)
        return ClassSession.objects.none()

    def perform_create(self, serializer):
        serializer.save()


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return AttendanceRecord.objects.all()
        if user.institution:
            return AttendanceRecord.objects.filter(student__institution=user.institution)
        return AttendanceRecord.objects.none()


class ProjectGroupViewSet(viewsets.ModelViewSet):
    queryset = ProjectGroup.objects.all()
    serializer_class = ProjectGroupSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return ProjectGroup.objects.all()
        if user.institution:
            return ProjectGroup.objects.filter(course__institution=user.institution)
        return ProjectGroup.objects.none()

    def perform_create(self, serializer):
        serializer.save()


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Task.objects.all()
        if user.institution:
            return Task.objects.filter(group__course__institution=user.institution)
        return Task.objects.none()


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Quiz.objects.all()
        if user.institution:
            return Quiz.objects.filter(course__institution=user.institution)
        return Quiz.objects.none()

    def perform_create(self, serializer):
        serializer.save()


class QuizAttemptViewSet(viewsets.ModelViewSet):
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return QuizAttempt.objects.all()
        if user.institution:
            return QuizAttempt.objects.filter(student__institution=user.institution)
        return QuizAttempt.objects.none()


class AttemptAnswerViewSet(viewsets.ModelViewSet):
    queryset = AttemptAnswer.objects.all()
    serializer_class = AttemptAnswerSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return AttemptAnswer.objects.all()
        if user.institution:
            return AttemptAnswer.objects.filter(attempt__student__institution=user.institution)
        return AttemptAnswer.objects.none()
