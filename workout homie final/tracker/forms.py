from django import forms
from .models import Goal, DailyLog, Workout


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["name", "start_weight", "target_weight", "weeks_total", "weeks_in"]


class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = [
            "date",
            "move_cal", "move_goal",
            "exercise_min", "exercise_goal",
            "stand_hrs", "stand_goal",
            "calories",
            "weight",
            "water_cups", "water_goal",
            "steps", "steps_goal",
        ]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ["date", "name", "category", "start_time", "duration_min", "calories"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
        }