# Quick Start Guide

Get up and running with Exercise Tracker in under 5 minutes.

## Setup (3 commands)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
streamlit run app.py
```

Open browser to http://localhost:8501

## Your First Workout (5 steps)

### Step 1: Create an Exercise (1 minute)

1. Navigate to **Exercise Library** page
2. Fill out form:
   - Name: "Barbell Squat"
   - Primary muscles: Select "Quadriceps" and "Glutes"
   - Progression scheme: "Rep Range"
   - Rep range: Min=8, Max=12
   - Weight increment: 5
   - Enable warmup: ✓ (checked)
3. Click **Create Exercise**

Repeat for 2-3 more exercises (Bench Press, Deadlift, etc.)

### Step 2: Create a Workout (30 seconds)

1. Navigate to **Create Workout** page
2. Fill out form:
   - Name: "Leg Day"
   - Select exercises: Choose "Barbell Squat" (and any others you created)
3. Click **Create Workout**

### Step 3: Start Workout (10 seconds)

1. Navigate to **Workout Overview** page
2. Find "Leg Day" in the list
3. Click **Start Workout**

You're now in the workout execution page!

### Step 4: Execute Workout (5-60 minutes)

The app shows:
- Warmup sets (if configured): 1-3 sets based on intensity
- Working sets: 3 sets with target weight and reps

For your **first workout** of an exercise:
- Default starting weight is 45 lbs
- Click "Adjust Weight/Reps" to set appropriate starting weight

For each set:
1. Perform the set
2. Check the "Completed" box ✓
3. (Optional) Override weight/reps if you used different values
4. Rest, then move to next set

When all working sets are done:
- Click **Complete Workout**
- View summary statistics

### Step 5: Track Progress (30 seconds)

1. Navigate to **History** page
2. See your completed workout
3. Expand to view set-by-set details

**Next Workout:**
When you do "Leg Day" again, the app automatically:
- Remembers your last performance
- Calculates next weight/reps based on progression logic
- Generates appropriate warmup sets

## Understanding Progression

### Rep Range Example

**Workout 1:** 135 lbs × 8 reps ✓ → Success
**Workout 2:** 135 lbs × 9 reps ✓ → Success (added 1 rep)
**Workout 3:** 135 lbs × 10 reps ✓ → Success (added 1 rep)
**Workout 4:** 135 lbs × 11 reps ✓ → Success
**Workout 5:** 135 lbs × 12 reps ✓ → Success (hit max)
**Workout 6:** 140 lbs × 8 reps ✓ → Success (weight up, reps reset)

Progress by adding reps until you hit max, then increase weight.

### Linear Weight Example

**Workout 1:** 225 lbs × 5 reps ✓ → Success
**Workout 2:** 230 lbs × 5 reps ✓ → Success (added 5 lbs)
**Workout 3:** 235 lbs × 5 reps ✓ → Success (added 5 lbs)
**Workout 4:** 240 lbs × 5 reps ✗ → Failure (couldn't complete all sets)
**Workout 5:** 240 lbs × 5 reps ✓ → Success (retry same weight)
**Workout 6:** 245 lbs × 5 reps ✓ → Success (added 5 lbs)

Progress by adding weight each successful workout, keep reps constant.

## Pro Tips

### Choosing Progression Scheme

- **Rep Range (8-12)**: Best for hypertrophy (muscle building)
- **Linear Weight (5 reps)**: Best for strength development
- **Linear Weight (3 reps)**: Best for max strength

### When to Enable Warmups

✓ **Enable for**: Squats, Deadlifts, Bench Press (compound movements)
✗ **Disable for**: Bicep Curls, Lateral Raises (isolation exercises)

### Setting Starting Weights

First time doing an exercise:
1. Use "Adjust Weight/Reps" to override the 45 lb default
2. Start conservative - better to be too light than too heavy
3. Future workouts will progress automatically from there

### Recording Failed Sets

If you can't complete a set:
1. Still check it as "Completed"
2. Use "Adjust Weight/Reps" to enter actual reps achieved
3. Next workout will repeat the same weight (no progression)

### Backup Your Data

Your workout history is valuable! Backup regularly:

```bash
# Quick backup
cp -r data/ data_backup_$(date +%Y%m%d)
```

## Common Actions

### View Exercise Details
Exercise Library → Click exercise name or expand details

### See Last Workout Performance
Workout Execution → Each exercise shows "Last Time" data

### Filter History
History → Use date range, workout, or exercise filters at top

### Check 1RM Estimates
History → Expand workout → View per-set 1RM estimates

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| App won't start | Activate virtual environment: `source venv/bin/activate` |
| Changes not saving | Check terminal for errors, verify `data/` directory exists |
| Workout won't progress | Complete all working sets (warmups optional) |
| Starting weight wrong | Use "Adjust Weight/Reps" on first workout |
| Session state lost | Don't refresh browser during workout |

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed help.

## Next Steps

Now that you're up and running:

1. **Create more exercises**: Build out your exercise library
2. **Create multiple workouts**: Push Day, Pull Day, Leg Day, etc.
3. **Track consistently**: Execute and complete workouts regularly
4. **Review progress**: Check History page to see your progression over time

## Data Location

All your data is stored in CSV files in the `data/` directory:
- `exercises.csv` - Your exercise library
- `workouts.csv` - Your workout templates
- `workout_logs.csv` - Completed workout sessions
- `set_logs.csv` - Individual set records

## Need More Help?

- **Detailed guide**: [README.md](library/software/external_libraries/agent-os/agent-os-sandbox/exercise_module/README.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Known issues**: [KNOWN_ISSUES.md](KNOWN_ISSUES.md)

## That's It!

You're now ready to track your workouts and make consistent gains. The app handles all the progression logic automatically - just show up and lift!
