from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Institution(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=100, unique=True)
    logo_url = models.URLField(blank=True, null=True)
    security_policies = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'System Super Admin'),
        ('inst_admin', 'Institution Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


class Course(models.Model):
    title = models.CharField(max_length=255)
    course_code = models.CharField(max_length=20, default='')
    description = models.TextField(blank=True, null=True)
    syllabus = models.TextField(blank=True, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='courses')
    enrollment_key = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_code} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} -> {self.course.title}"


class Grade(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_grades')
    grade = models.CharField(max_length=10)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}: {self.grade}"


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_limit = models.IntegerField(default=60)
    total_points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    due_date = models.DateTimeField(null=True, blank=True)
    allow_multiple_attempts = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=500)
    options = models.JSONField()
    correct_answer_index = models.IntegerField()
    points = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} attempt on {self.quiz.title}"


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer_index = models.IntegerField()
    is_correct = models.BooleanField(default=False)
    points_earned = models.IntegerField(default=0)

    def __str__(self):
        return f"Answer to {self.question.id} by {self.attempt.student.username}"


class ClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255, default='Live Session')
    date = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    meeting_link = models.URLField(blank=True, default='')
    recording_url = models.URLField(blank=True, default='')
    is_live = models.BooleanField(default=False)
    qr_code_uuid = models.CharField(max_length=255, unique=True)
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    allowed_radius_meters = models.IntegerField(default=50)

    def __str__(self):
        return f"{self.title} - {self.course.title}"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.session.course.title}: {self.get_status_display()}"


class ProjectGroup(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='project_groups')
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='agile_groups')

    def __str__(self):
        return f"{self.name} ({self.course.title})"


class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    )
    group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"


class Assignment(models.Model):
    TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('group', 'Group'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    due_date = models.DateTimeField(null=True, blank=True)
    max_points = models.IntegerField(default=100)
    assignment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='individual')
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    groups = models.ManyToManyField(ProjectGroup, blank=True, related_name='assignments')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(ProjectGroup, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, default='')
    is_late = models.BooleanField(default=False)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.username if self.student else 'Group'} - {self.assignment.title}"


class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, default='')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


