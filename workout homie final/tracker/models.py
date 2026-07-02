from django.db import models


class Goal(models.Model):
    name = models.CharField(max_length=100)
    start_weight = models.FloatField()
    target_weight = models.FloatField()
    weeks_total = models.IntegerField()
    weeks_in = models.IntegerField(default=0)

    @property
    def percent_complete(self):
        total_to_lose = self.start_weight - self.target_weight
        if total_to_lose <= 0:
            return 0
        latest = DailyLog.objects.order_by("-date").first()
        if not latest:
            return 0
        lost_so_far = self.start_weight - latest.weight
        pct = (lost_so_far / total_to_lose) * 100
        return max(0, min(100, round(pct)))

    def __str__(self):
        return self.name


class DailyLog(models.Model):
    date = models.DateField(unique=True)

    move_cal = models.IntegerField(default=0)
    move_goal = models.IntegerField(default=500)
    exercise_min = models.IntegerField(default=0)
    exercise_goal = models.IntegerField(default=30)
    stand_hrs = models.IntegerField(default=0)
    stand_goal = models.IntegerField(default=12)

    calories = models.IntegerField(default=0)
    weight = models.FloatField()
    water_cups = models.IntegerField(default=0)
    water_goal = models.IntegerField(default=8)
    steps = models.IntegerField(default=0)
    steps_goal = models.IntegerField(default=10000)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return str(self.date)


class Workout(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    start_time = models.TimeField()
    duration_min = models.IntegerField()
    calories = models.IntegerField()

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.name