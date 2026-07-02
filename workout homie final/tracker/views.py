import math
from datetime import date, timedelta
from django.shortcuts import render, redirect
from .models import Goal, DailyLog, Workout
from .forms import GoalForm, DailyLogForm, WorkoutForm


def make_ring(value, goal, radius, color):
    pct = min(value / goal, 1) * 100 if goal else 0
    circumference = 2 * math.pi * radius
    dash = circumference * pct / 100
    return {
        "pct": round(pct),
        "radius": radius,
        "circ": round(circumference, 1),
        "dash": round(dash, 1),
        "color": color,
    }


def dashboard(request):
    if request.method == "POST":
        if "submit_goal" in request.POST:
            form = GoalForm(request.POST)
            if form.is_valid():
                form.save()
            return redirect("dashboard")

        if "submit_log" in request.POST:
            form = DailyLogForm(request.POST)
            if form.is_valid():
                form.save()
            return redirect("dashboard")

        if "submit_workout" in request.POST:
            form = WorkoutForm(request.POST)
            if form.is_valid():
                form.save()
            return redirect("dashboard")

    today = date.today()
    goal = Goal.objects.last()
    log = DailyLog.objects.filter(date=today).first()
    workouts = Workout.objects.filter(date=today)

    # activity rings
    rings = None
    if log:
        rings = [
            make_ring(log.move_cal, log.move_goal, 40, "#ff453a"),
            make_ring(log.exercise_min, log.exercise_goal, 32, "#32d74b"),
            make_ring(log.stand_hrs, log.stand_goal, 24, "#0a84ff"),
        ]

    # compare to yesterday / last week
    yesterday_log = DailyLog.objects.filter(date=today - timedelta(days=1)).first()
    week_ago_log = DailyLog.objects.filter(date=today - timedelta(days=7)).first()
    calorie_diff = (log.calories - yesterday_log.calories) if (log and yesterday_log) else None
    weight_diff = (log.weight - week_ago_log.weight) if (log and week_ago_log) else None

    # this week's calendar strip (Sunday - Saturday)
    offset = (today.weekday() + 1) % 7
    start_of_week = today - timedelta(days=offset)
    week_days = []
    for i in range(7):
        d = start_of_week + timedelta(days=i)
        week_days.append({
            "num": d.day,
            "has_log": DailyLog.objects.filter(date=d).exists(),
            "is_today": d == today,
        })

    # water cups row
    water_range = range(log.water_goal) if log else range(8)

    # weight trend chart (last 8 logged days)
    recent_logs = list(DailyLog.objects.order_by("-date")[:8])
    recent_logs.reverse()
    trend = []
    if recent_logs:
        weights = [l.weight for l in recent_logs]
        min_w, max_w = min(weights), max(weights)
        span = (max_w - min_w) or 1
        for l in recent_logs:
            height_pct = 20 + (l.weight - min_w) / span * 80
            trend.append({
                "weight": l.weight,
                "height_pct": round(height_pct),
                "is_today": l.date == today,
            })

    context = {
        "goal": goal,
        "log": log,
        "workouts": workouts,
        "rings": rings,
        "calorie_diff": calorie_diff,
        "weight_diff": weight_diff,
        "week_days": week_days,
        "water_range": water_range,
        "trend": trend,
        "goal_form": GoalForm(),
        "log_form": DailyLogForm(initial={"date": today}),
        "workout_form": WorkoutForm(initial={"date": today}),
    }
    return render(request, "tracker/dashboard.html", context)