from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (UserProfile, Course, Enrollment, Grade, Quiz, Question, 
                     QuizAttempt, AttemptAnswer, ClassSession, AttendanceRecord, 
                     ProjectGroup, Task)

# --- CORE USERS & COURSES ---
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'created_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']

class GradeSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Grade
        fields = ['id', 'course', 'grade', 'assigned_at']

# --- ADVANCED ATTENDANCE ---
class ClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = '__all__'

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    class Meta:
        model = AttendanceRecord
        fields = '__all__'

# --- AGILE WORKSPACE ---
class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    class Meta:
        model = Task
        fields = '__all__'

class ProjectGroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True) # Pulls all tasks for this group
    class Meta:
        model = ProjectGroup
        fields = ['id', 'name', 'course', 'members', 'tasks']

# --- QUIZZES ---
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
    # This pulls in all the student's individual answers for this attempt
    answers = AttemptAnswerSerializer(many=True, read_only=True) 

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'student', 'score', 'total_points', 'percentage', 'started_at', 'submitted_at', 'time_spent', 'is_completed', 'answers']