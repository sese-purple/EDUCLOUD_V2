from django.contrib import admin
from .models import UserProfile, Course, Enrollment, Grade, Quiz, Question, QuizAttempt, AttemptAnswer , ClassSession, AttendanceRecord, ProjectGroup, Task

# This tells the Admin panel to display all of these tables
admin.site.register(UserProfile)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Grade)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizAttempt)
admin.site.register(AttemptAnswer)
admin.site.register(ClassSession)
admin.site.register(AttendanceRecord)
admin.site.register(ProjectGroup)
admin.site.register(Task)