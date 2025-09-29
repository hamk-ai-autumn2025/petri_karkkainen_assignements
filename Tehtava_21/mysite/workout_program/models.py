from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class MuscleGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    EXERCISE_TYPES = [
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('flexibility', 'Flexibility'),
        ('balance', 'Balance'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    muscle_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE, null=True, blank=True)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    equipment_needed = models.TextField(blank=True)
    difficulty_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Difficulty level from 1 (easy) to 5 (hard)"
    )

    def __str__(self):
        return self.name

class WorkoutProgram(models.Model):
    PROGRAM_TYPES = [
        ('muscle', 'Muscle Building'),
        ('weight_loss', 'Weight Loss'),
        ('cardio', 'Cardio Training'),
        ('general', 'General Fitness'),
        ('strength', 'Strength Training'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    duration_weeks = models.IntegerField(validators=[MinValueValidator(1)])
    difficulty_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Program difficulty level from 1 (easy) to 5 (hard)"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.get_program_type_display()}"

class WorkoutDay(models.Model):
    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name='workout_days')
    day_number = models.IntegerField(validators=[MinValueValidator(1)])
    day_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['program', 'day_number']
        ordering = ['day_number']

    def __str__(self):
        return f"{self.program.name} - Day {self.day_number} : {self.day_name}"

class WorkoutSession(models.Model):
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='workout_sessions')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField(validators=[MinValueValidator(1)])
    repetitions = models.IntegerField(validators=[MinValueValidator(1)], help_text="Reps per set")
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        help_text="Duration in minutes (for cardio exercises)"
    )
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kg (for strength exercises)"
    )
    rest_seconds = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=60,
        help_text="Rest time between sets in seconds"
    )
    order = models.IntegerField(default=1, help_text="Order of exercise in the session")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.exercise.name} - {self.sets} x {self.repetitions}"
    
class UserWorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE)
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE)
    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    completed_sets = models.IntegerField(null=True, blank=True)
    completed_reps = models.IntegerField(null=True, blank=True)
    completed_weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    duration_minutes = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        status = "Completed" if self.is_completed else "Pending"
        return f"{self.user.username} - {self.workout_session.exercise.name} ({status})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height_cm = models.IntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    fitness_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Current fitness level from 1 (beginner) to 5 (advanced)"
    )
    goals = models.TextField(blank=True, help_text="Fitness goals")

    def __str__(self):
        return f"{self.user.username}'s Profile"
