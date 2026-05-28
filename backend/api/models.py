from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 👥 USER PROFILE (Handling Roles)
# ==========================================
# Since Django provides a built-in User table with email/password, 
# we link a Profile to it to hold your custom 'role' field.
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# ==========================================
# 📚 COURSES & ENROLLMENTS
# ==========================================
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course') # Prevents double enrollment

    def __str__(self):
        return f"{self.student.username} -> {self.course.title}"

# ==========================================
# 📝 GRADES
# ==========================================
class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_grades')
    grade = models.CharField(max_length=10) # e.g., 'A', 'B+', '95%'
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course') # One final grade per student per course

    def __str__(self):
        return f"{self.student.username} - {self.course.title}: {self.grade}"

# ==========================================
# ❓ QUIZZES & QUESTIONS
# ==========================================
class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    time_limit = models.IntegerField(default=60) # In minutes
    total_points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    due_date = models.DateTimeField(null=True, blank=True)
    allow_multiple_attempts = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"

# This replaces the embedded array in your Mongoose schema
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=500)
    options = models.JSONField() # Stores an array of strings like ["A", "B", "C", "D"]
    correct_answer_index = models.IntegerField()
    points = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text

# ==========================================
# 📊 QUIZ ATTEMPTS
# ==========================================
class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(default=0) # In minutes
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} attempt on {self.quiz.title}"

# This replaces the embedded answers array inside your old QuizAttempt
class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer_index = models.IntegerField()
    is_correct = models.BooleanField(default=False)
    points_earned = models.IntegerField(default=0)

    def __str__(self):
        return f"Answer to {self.question.id} by {self.attempt.student.username}"
    

# ==========================================
# 📍 ADVANCED ATTENDANCE & PROCTORING
# ==========================================
class ClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateTimeField(auto_now_add=True)
    qr_code_uuid = models.CharField(max_length=255, unique=True) # The dynamic QR string
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    allowed_radius_meters = models.IntegerField(default=50) # How close they need to be to check in

    def __str__(self):
        return f"{self.course.title} Session - {self.date.strftime('%Y-%m-%d')}"

class AttendanceRecord(models.Model):
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'student') # One check-in per student per session

    def __str__(self):
        return f"{self.student.username} - {self.session.course.title} Check-in"

# ==========================================
# 🚀 AGILE WORKSPACE (GROUP PROJECTS)
# ==========================================
class ProjectGroup(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='project_groups')
    name = models.CharField(max_length=255)
    
    # ManyToManyField is perfect here because one group has many users, 
    # and one user can be in many groups.
    members = models.ManyToManyField(User, related_name='agile_groups')

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
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"