from rest_framework import serializers
from .models import (Institution, User, Course, Enrollment, Grade, Quiz, Question,
                     QuizAttempt, AttemptAnswer, ClassSession, AttendanceRecord,
                     ProjectGroup, Task)


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'institution', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    instructor_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    institution = InstitutionSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'course_code', 'description', 'institution', 'instructor', 'instructor_id', 'created_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']


class GradeSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'student', 'course', 'grade', 'assigned_at']


class ClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = '__all__'


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


class ProjectGroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectGroup
        fields = ['id', 'name', 'course', 'members', 'tasks']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'course', 'time_limit', 'total_points', 'questions']


class AttemptAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptAnswer
        fields = '__all__'


class QuizAttemptSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    quiz = QuizSerializer(read_only=True)
    answers = AttemptAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'student', 'score', 'total_points', 'percentage', 'started_at', 'submitted_at', 'time_spent', 'is_completed', 'answers']
