from rest_framework import serializers
from .models import (Institution, User, Course, Enrollment, Grade, Quiz, Question,
                     QuizAttempt, AttemptAnswer, ClassSession, AttendanceRecord,
                     ProjectGroup, Task, Assignment, Submission, Material)


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
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'course_code', 'description', 'syllabus', 'enrollment_key',
                  'institution', 'instructor', 'instructor_id', 'is_enrolled', 'created_at', 'updated_at']

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Enrollment.objects.filter(student=request.user, course=obj).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'student':
            data.pop('enrollment_key', None)
        return data


class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']


class GradeSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    student_id = serializers.IntegerField(write_only=True)
    course_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'student', 'course', 'student_id', 'course_id', 'grade', 'assigned_at']

    def create(self, validated_data):
        validated_data.pop('student_id')
        validated_data.pop('course_id')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('student_id', None)
        validated_data.pop('course_id', None)
        return super().update(instance, validated_data)


class ClassSessionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

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


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = '__all__'

    def get_student_name(self, obj):
        if obj.student:
            return f"{obj.student.first_name} {obj.student.last_name}"
        return None


class MaterialSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = Material
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    instructor = UserSerializer(read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'course', 'time_limit', 'total_points',
                  'is_active', 'due_date', 'allow_multiple_attempts', 'instructor', 'questions']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'student':
            review = request.query_params.get('review') == '1'
            if not review and data.get('questions'):
                for q in data['questions']:
                    q.pop('correct_answer_index', None)
        return data


class AttemptAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptAnswer
        fields = '__all__'


class QuizAttemptSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    quiz = QuizSerializer(read_only=True)
    answers = AttemptAnswerSerializer(many=True, read_only=True)
    quiz_id = serializers.IntegerField(write_only=True)
    student_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'student', 'quiz_id', 'student_id', 'score', 'total_points',
                  'percentage', 'started_at', 'submitted_at', 'time_spent', 'is_completed', 'answers']
