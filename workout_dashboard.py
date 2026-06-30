from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "workout-secret"

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My Workout Homie</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0e0e0e; color: #fff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 16px; max-width: 480px; margin: 0 auto; }
  h1 { font-size: 26px; margin-bottom: 4px; }
  h1 span { color: #f59e0b; }
  .sub { color: #888; font-size: 13px; margin-bottom: 20px; }

  /* Goal card */
  .goal-card { background: #1a1a1a; border-radius: 14px; padding: 16px 20px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
  .goal-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: .5px; }
  .goal-title { font-size: 20px; font-weight: 700; }
  .goal-sub { font-size: 12px; color: #888; margin-top: 2px; }
  .goal-pct { font-size: 30px; font-weight: 700; color: #f59e0b; text-align: right; }
  .goal-pct span { display: block; font-size: 11px; color: #888; font-weight: 400; }

  /* Activity rings */
  .rings-card { background: #1a1a1a; border-radius: 14px; padding: 16px 20px; margin-bottom: 12px; display: flex; align-items: center; gap: 20px; }
  .rings-info { flex: 1; }
  .ring-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
  .ring-row:last-child { margin-bottom: 0; }
  .ring-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }
  .ring-label { font-size: 13px; color: #ccc; }
  .ring-pct { font-size: 13px; font-weight: 600; }
  svg.rings { width: 90px; height: 90px; flex-shrink: 0; }

  /* Stat grid */
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
  .stat-card { background: #1a1a1a; border-radius: 14px; padding: 16px; }
  .stat-icon { font-size: 20px; margin-bottom: 6px; }
  .stat-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: .5px; }
  .stat-value { font-size: 26px; font-weight: 700; line-height: 1.1; }
  .stat-unit { font-size: 13px; font-weight: 400; }
  .stat-sub { font-size: 12px; margin-top: 4px; }
  .up { color: #f59e0b; } .down { color: #34d399; } .warn { color: #f59e0b; }
  .bar-bg { background: #2a2a2a; border-radius: 4px; height: 5px; margin-top: 10px; }
  .bar-fill { height: 5px; border-radius: 4px; }

  /* Workouts */
  .section-header { display: flex; justify-content: space-between; align-items: center; margin: 20px 0 10px; }
  .section-title { font-size: 18px; font-weight: 700; }
  .workout-card { background: #1a1a1a; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
  .workout-icon { font-size: 28px; margin-right: 12px; }
  .workout-name { font-size: 15px; font-weight: 600; }
  .workout-detail { font-size: 12px; color: #888; margin-top: 2px; }
  .workout-cal { font-size: 14px; font-weight: 600; color: #f59e0b; }

  /* Water */
  .water-card { background: #1a1a1a; border-radius: 14px; padding: 16px 20px; margin-bottom: 12px; }
  .water-header { display: flex; justify-content: space-between; margin-bottom: 12px; }
  .water-cups { display: flex; gap: 6px; flex-wrap: wrap; }
  .cup { width: 36px; height: 36px; border-radius: 8px; background: #38bdf8; opacity: 0.25; }
  .cup.filled { opacity: 1; }

  /* Form */
  .form-card { background: #1a1a1a; border-radius: 14px; padding: 20px; margin-bottom: 12px; flex: 1; min-width: 280px; }
  .form-card h2 { font-size: 16px; font-weight: 700; margin-bottom: 16px; color: #f59e0b; }
  .form-section { font-size: 12px; text-transform: uppercase; color: #888; letter-spacing: .5px; margin: 14px 0 8px; }
  label { display: block; font-size: 13px; color: #ccc; margin-bottom: 4px; margin-top: 10px; }
  input { width: 100%; background: #2a2a2a; border: 1px solid #333; border-radius: 8px; color: #fff; padding: 10px 12px; font-size: 14px; }
  input:focus { outline: none; border-color: #f59e0b; }
  button[type=submit] { width: 100%; margin-top: 20px; background: #f59e0b; color: #000; border: none; border-radius: 10px; padding: 13px; font-size: 15px; font-weight: 700; cursor: pointer; }
  button[type=submit]:hover { background: #fbbf24; }
  .edit-btn { background: #2a2a2a; border: none; color: #f59e0b; font-size: 13px; padding: 6px 12px; border-radius: 8px; cursor: pointer; }
</style>
</head>
<body>

{% if not data %}
<!-- INPUT FORM -->
<div style="padding-top:10px; display:flex; flex-wrap:wrap; gap:12px; align-items:flex-start">
  <h1>My Workout <span>Homie</span> 💪</h1>
  <p class="sub">Enter your stats to see your dashboard</p>
  <form method="POST" action="/save">
    <div class="form-card">
      <h2>👤 Personal</h2>
      <label>Your Name</label>
      <input name="name" placeholder="Jordan" required>
      <label>Current Goal</label>
      <input name="goal" placeholder="Lose Weight" required>
      <label>Goal Progress (%)</label>
      <input name="goal_pct" type="number" min="0" max="100" placeholder="73" required>
      <label>Pounds to Target</label>
      <input name="lbs_to_target" type="number" placeholder="8" required>
      <label>Weeks In</label>
      <input name="weeks_in" type="number" placeholder="14" required>
    </div>

    <div class="form-card">
      <h2>🏃 Activity Rings</h2>
      <label>Move (calories burned)</label>
      <input name="move_current" type="number" placeholder="420" required>
      <label>Move Goal (calories)</label>
      <input name="move_goal" type="number" placeholder="500" required>
      <label>Exercise (minutes done)</label>
      <input name="exercise_current" type="number" placeholder="28" required>
      <label>Exercise Goal (minutes)</label>
      <input name="exercise_goal" type="number" placeholder="30" required>
      <label>Stand (hours done)</label>
      <input name="stand_current" type="number" placeholder="9" required>
      <label>Stand Goal (hours)</label>
      <input name="stand_goal" type="number" placeholder="12" required>
    </div>

    <div class="form-card">
      <h2>📊 Today's Stats</h2>
      <label>Calories Eaten (kcal)</label>
      <input name="calories" type="number" placeholder="1840" required>
      <label>Calories vs Yesterday (+ or -)</label>
      <input name="cal_diff" type="number" placeholder="120" required>
      <label>Current Weight (lbs)</label>
      <input name="weight" type="number" step="0.1" placeholder="172" required>
      <label>Weight Change This Week (lbs, use - for loss)</label>
      <input name="weight_diff" type="number" step="0.1" placeholder="-0.4" required>
      <label>Water (cups drunk today)</label>
      <input name="water_current" type="number" placeholder="6" required>
      <label>Water Goal (cups)</label>
      <input name="water_goal" type="number" placeholder="8" required>
      <label>Steps Today</label>
      <input name="steps" type="number" placeholder="7342" required>
      <label>Step Goal</label>
      <input name="steps_goal" type="number" placeholder="10000" required>
    </div>

    <div class="form-card">
      <h2>🏋️ Today's Workouts</h2>
      <p class="form-section">Workout 1</p>
      <label>Name</label>
      <input name="w1_name" placeholder="Upper Body Strength">
      <label>Time & Duration</label>
      <input name="w1_time" placeholder="8:30 AM · 42 min">
      <label>Type</label>
      <input name="w1_type" placeholder="Chest, Arms">
      <label>Calories</label>
      <input name="w1_cal" type="number" placeholder="340">

      <p class="form-section">Workout 2 (optional)</p>
      <label>Name</label>
      <input name="w2_name" placeholder="Morning Walk">
      <label>Time & Duration</label>
      <input name="w2_time" placeholder="7:00 AM · 25 min">
      <label>Type</label>
      <input name="w2_type" placeholder="Cardio">
      <label>Calories</label>
      <input name="w2_cal" type="number" placeholder="80">
    </div>

    <button type="submit">Show My Dashboard →</button>
  </form>
</div>

{% else %}
<!-- DASHBOARD -->
<p class="sub" style="margin-bottom:6px">GOOD MORNING</p>
<h1 style="margin-bottom:2px">Let's get it, <span>{{ data.name }}</span> 💪</h1>
<div class="sub" style="margin-bottom:16px">{{ data.date }}</div>

<!-- Goal -->
<div class="goal-card">
  <div>
    <div class="goal-label">Current Goal</div>
    <div class="goal-title">{{ data.goal }}</div>
    <div class="goal-sub">–{{ data.lbs_to_target }} lbs to target · {{ data.weeks_in }} weeks in</div>
  </div>
  <div class="goal-pct">{{ data.goal_pct }}%<span>complete</span></div>
</div>

<!-- Activity Rings -->
<div class="rings-card">
  <!-- Simple ring SVG -->
  <svg class="rings" viewBox="0 0 90 90">
    {% set cx=45 %} {% set cy=45 %}
    {% for ring in data.rings %}
    <circle cx="{{ cx }}" cy="{{ cy }}" r="{{ ring.r }}" fill="none" stroke="#2a2a2a" stroke-width="7"/>
    <circle cx="{{ cx }}" cy="{{ cy }}" r="{{ ring.r }}" fill="none" stroke="{{ ring.color }}" stroke-width="7"
      stroke-dasharray="{{ ring.dash }} {{ ring.gap }}" stroke-dashoffset="{{ ring.offset }}" stroke-linecap="round"/>
    {% endfor %}
  </svg>
  <div class="rings-info">
    <div class="ring-row">
      <div><span class="ring-dot" style="background:#ef4444"></span><span class="ring-label">Move <small style="color:#888">{{ data.move_current }}/{{ data.move_goal }} cal</small></span></div>
      <div class="ring-pct">{{ data.move_pct }}%</div>
    </div>
    <div class="ring-row">
      <div><span class="ring-dot" style="background:#22c55e"></span><span class="ring-label">Exercise <small style="color:#888">{{ data.exercise_current }}/{{ data.exercise_goal }} min</small></span></div>
      <div class="ring-pct">{{ data.exercise_pct }}%</div>
    </div>
    <div class="ring-row">
      <div><span class="ring-dot" style="background:#38bdf8"></span><span class="ring-label">Stand <small style="color:#888">{{ data.stand_current }}/{{ data.stand_goal }} hrs</small></span></div>
      <div class="ring-pct">{{ data.stand_pct }}%</div>
    </div>
  </div>
</div>

<!-- Stats Grid -->
<div class="grid2">
  <div class="stat-card">
    <div class="stat-icon">🔥</div>
    <div class="stat-label">Calories</div>
    <div class="stat-value">{{ data.calories }}<span class="stat-unit">kcal</span></div>
    <div class="stat-sub {% if data.cal_diff > 0 %}up{% else %}down{% endif %}">
      {{ "↑" if data.cal_diff > 0 else "↓" }} {{ data.cal_diff|abs }} from yesterday
    </div>
    <div class="bar-bg"><div class="bar-fill" style="width:{{ [data.calories/2500*100,100]|min }}%; background:linear-gradient(90deg,#ef4444,#22c55e)"></div></div>
  </div>
  <div class="stat-card">
    <div class="stat-icon">⚖️</div>
    <div class="stat-label">Weight</div>
    <div class="stat-value">{{ data.weight }}<span class="stat-unit">lbs</span></div>
    <div class="stat-sub {% if data.weight_diff < 0 %}down{% else %}up{% endif %}">
      {{ "↓" if data.weight_diff < 0 else "↑" }} {{ data.weight_diff|abs }} lbs this week
    </div>
    <div class="bar-bg"><div class="bar-fill" style="width:{{ data.goal_pct }}%; background:#34d399"></div></div>
  </div>
  <div class="stat-card">
    <div class="stat-icon">💧</div>
    <div class="stat-label">Water</div>
    <div class="stat-value">{{ data.water_current }}<span class="stat-unit">/{{ data.water_goal }} cups</span></div>
    <div class="stat-sub" style="color:#888">{{ [data.water_goal - data.water_current, 0]|max }} more to go</div>
    <div class="bar-bg"><div class="bar-fill" style="width:{{ data.water_current/data.water_goal*100 }}%; background:#38bdf8"></div></div>
  </div>
  <div class="stat-card">
    <div class="stat-icon">👟</div>
    <div class="stat-label">Steps</div>
    <div class="stat-value">{{ "{:,}".format(data.steps) }}</div>
    <div class="stat-sub warn">↑ Goal: {{ "{:,}".format(data.steps_goal) }}</div>
    <div class="bar-bg"><div class="bar-fill" style="width:{{ [data.steps/data.steps_goal*100,100]|min }}%; background:#f59e0b"></div></div>
  </div>
</div>

<!-- Water cups -->
<div class="water-card">
  <div class="water-header">
    <span>💧 Water today</span>
    <span style="color:#38bdf8">{{ data.water_current }} of {{ data.water_goal }} cups</span>
  </div>
  <div class="water-cups">
    {% for i in range(data.water_goal) %}
    <div class="cup {% if i < data.water_current %}filled{% endif %}"></div>
    {% endfor %}
  </div>
</div>

<!-- Workouts -->
<div class="section-header">
  <div class="section-title">Today's Workouts</div>
</div>
{% for w in data.workouts %}
<div class="workout-card">
  <div style="display:flex;align-items:center">
    <div class="workout-icon">{{ w.icon }}</div>
    <div>
      <div class="workout-name">{{ w.name }}</div>
      <div class="workout-detail">{{ w.time }} · {{ w.type }}</div>
    </div>
  </div>
  <div class="workout-cal">{{ w.cal }} cal</div>
</div>
{% endfor %}

<!-- Edit button -->
<div style="text-align:center;margin:24px 0 16px">
  <form method="POST" action="/reset">
    <button type="submit" class="edit-btn">✏️ Edit My Stats</button>
  </form>
</div>
{% endif %}

</body>
</html>
"""

import math
from datetime import datetime

def calc_ring(pct, r):
    circ = 2 * math.pi * r
    dash = circ * min(pct / 100, 1)
    return {"r": r, "dash": round(dash, 2), "gap": round(circ, 2), "offset": round(circ / 4, 2)}

WORKOUT_ICONS = {
    "strength": "🏋️", "walk": "🚶", "run": "🏃", "cardio": "❤️",
    "yoga": "🧘", "cycling": "🚴", "swim": "🏊", "default": "💪"
}

def get_icon(name, wtype):
    text = (name + wtype).lower()
    for key, icon in WORKOUT_ICONS.items():
        if key in text:
            return icon
    return WORKOUT_ICONS["default"]

@app.route("/")
def index():
    data = session.get("data")
    return render_template_string(HTML, data=data)

@app.route("/save", methods=["POST"])
def save():
    f = request.form
    move_pct  = round(int(f["move_current"])     / int(f["move_goal"])     * 100)
    exer_pct  = round(int(f["exercise_current"])  / int(f["exercise_goal"]) * 100)
    stand_pct = round(int(f["stand_current"])     / int(f["stand_goal"])    * 100)

    workouts = []
    for i in ("1", "2"):
        if f.get(f"w{i}_name"):
            workouts.append({
                "name": f[f"w{i}_name"],
                "time": f.get(f"w{i}_time", ""),
                "type": f.get(f"w{i}_type", ""),
                "cal":  f.get(f"w{i}_cal", "0"),
                "icon": get_icon(f[f"w{i}_name"], f.get(f"w{i}_type", "")),
            })

    session["data"] = {
        "name": f["name"],
        "date": datetime.now().strftime("%a, %B %d"),
        "goal": f["goal"],
        "goal_pct": int(f["goal_pct"]),
        "lbs_to_target": f["lbs_to_target"],
        "weeks_in": f["weeks_in"],
        "move_current": f["move_current"],
        "move_goal": f["move_goal"],
        "move_pct": move_pct,
        "exercise_current": f["exercise_current"],
        "exercise_goal": f["exercise_goal"],
        "exercise_pct": exer_pct,
        "stand_current": f["stand_current"],
        "stand_goal": f["stand_goal"],
        "stand_pct": stand_pct,
        "rings": [
            {**calc_ring(move_pct, 38),  "color": "#ef4444"},
            {**calc_ring(exer_pct, 29),  "color": "#22c55e"},
            {**calc_ring(stand_pct, 20), "color": "#38bdf8"},
        ],
        "calories": int(f["calories"]),
        "cal_diff": int(f["cal_diff"]),
        "weight": float(f["weight"]),
        "weight_diff": float(f["weight_diff"]),
        "water_current": int(f["water_current"]),
        "water_goal": int(f["water_goal"]),
        "steps": int(f["steps"]),
        "steps_goal": int(f["steps_goal"]),
        "workouts": workouts,
    }
    return redirect(url_for("index"))

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("data", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True)