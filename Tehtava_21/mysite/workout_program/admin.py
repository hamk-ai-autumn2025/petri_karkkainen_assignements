from django.contrib import admin
from .models import MuscleGroup, Exercise, WorkoutProgram, WorkoutDay, WorkoutSession, UserWorkoutLog, UserProfile

@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'exercise_type', 'muscle_group', 'difficulty_level']
    list_filter = ['exercise_type', 'muscle_group', 'difficulty_level']
    search_fields = ['name', 'description']

class WorkoutSessionInline(admin.TabularInline):
    model = WorkoutSession
    extra = 1

@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    list_display = ['program', 'day_number', 'day_name']
    list_filter = ['program']
    inlines = [WorkoutSessionInline]

@admin.register(WorkoutProgram)
class WorkoutProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'program_type', 'duration_weeks', 'difficulty_level', 'created_by', 'is_active']
    list_filter = ['program_type', 'difficulty_level', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = []

@admin.register(UserWorkoutLog)
class UserWorkoutLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise_name', 'completed_at', 'is_completed']
    list_filter = ['is_completed', 'completed_at', 'user']
    date_hierarchy = 'completed_at'

    def exercise_name(self, obj):
        return obj.workout_session.exercise.name
    exercise_name.short_description = 'Exercise'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'fitness_level', 'weight_kg']
    list_filter = ['fitness_level']
    search_fields = ['user__usename', 'user__first_name', 'user__last_name']

