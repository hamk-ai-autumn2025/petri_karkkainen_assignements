# workout_program/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import (
    WorkoutProgram, WorkoutDay, WorkoutSession, UserWorkoutLog,
    UserProfile, Exercise, MuscleGroup
)

def home(request):
    programs = WorkoutProgram.objects.filter(is_active=True)
    featured_programs = programs[:3]

    context = {
        'programs': programs,
        'featured_programs': featured_programs,
        'total_programs': programs.count(),
        'total_exercises': Exercise.objects.count(),
    }
    return render(request, 'workout_program/home.html', context)

def program_list(request):
    programs = WorkoutProgram.objects.filter(is_active=True)

    # Filter by program type
    program_type = request.GET.get('type')
    if program_type:
        programs = programs.filter(program_type=program_type)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        programs = programs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(programs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'program_types': WorkoutProgram.PROGRAM_TYPES,
        'current_type': program_type,
        'search_query': search_query,
    }
    return render(request, 'workout_program/program_list.html', context)

def program_detail(request, program_id):
    program = get_object_or_404(WorkoutProgram, id=program_id, is_active=True)
    workout_days = WorkoutDay.objects.filter(program=program).order_by('day_number')

    context = {
        'program': program,
        'workout_days': workout_days,
    }
    return render(request, 'workout_program/program_detail.html', context)

def workout_day_detail(request, program_id, day_id):
    workout_day = get_object_or_404(WorkoutDay, id=day_id, program_id=program_id)
    workout_sessions = WorkoutSession.objects.filter(workout_day=workout_day).order_by('order')

    context = {
        'workout_day': workout_day,
        'workout_sessions': workout_sessions,
    }
    return render(request, 'workout_program/workout_day_detail.html', context)

@login_required
def user_dashboard(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)

    # Get user's workout logs
    workout_logs = UserWorkoutLog.objects.filter(user=user).order_by('-completed_at')[:10]

    # Get active programs user is following
    active_logs = UserWorkoutLog.objects.filter(user=user, is_completed=True).values_list('program', flat=True).distinct()
    active_programs = WorkoutProgram.objects.filter(id__in=active_logs)

    context = {
        'profile': profile,
        'workout_logs': workout_logs,
        'active_programs': active_programs,
        'completed_workouts': workout_logs.count(),
    }
    return render(request, 'workout_program/user_dashboard.html', context)

@login_required
def log_workout(request, session_id):
    workout_session = get_object_or_404(WorkoutSession, id=session_id)

    if request.method == 'POST':
        completed_sets = request.POST.get('completed_sets')
        completed_reps = request.POST.get('completed_reps')
        completed_weight = request.POST.get('completed_weight')
        duration = request.POST.get('duration')
        notes = request.POST.get('notes', '')

        log = UserWorkoutLog.objects.create(
            user=request.user,
            workout_session=workout_session,
            workout_day=workout_session.workout_day,
            program=workout_session.workout_day.program,
            completed_sets=completed_sets,
            completed_reps=completed_reps,
            completed_weight_kg=completed_weight,
            duration_minutes=duration,
            notes=notes,
            is_completed=True
        )

        messages.success(request, f"Workout logged successfully: {workout_session.exercise.name}")
        return redirect('workout_day_detail',
                       program_id=workout_session.workout_day.program.id,
                       day_id=workout_session.workout_day.id)

    context = {
        'workout_session': workout_session,
    }
    return render(request, 'workout_program/log_workout.html', context)

def exercise_list(request):
    exercises = Exercise.objects.all()
    muscle_groups = MuscleGroup.objects.all()

    # Filter by muscle group
    muscle_group_id = request.GET.get('muscle_group')
    if muscle_group_id:
        exercises = exercises.filter(muscle_group_id=muscle_group_id)

    # Filter by exercise type
    exercise_type = request.GET.get('type')
    if exercise_type:
        exercises = exercises.filter(exercise_type=exercise_type)

    context = {
        'exercises': exercises,
        'muscle_groups': muscle_groups,
        'exercise_types': Exercise.EXERCISE_TYPES,
        'current_muscle_group': muscle_group_id,
        'current_type': exercise_type,
    }
    return render(request, 'workout_program/exercise_list.html', context)

def api_workout_progress(request):
    if request.user.is_authenticated:
        logs = UserWorkoutLog.objects.filter(user=request.user, is_completed=True)

        data = {
            'total_workouts': logs.count(),
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'Authentication required'}, status=401)
