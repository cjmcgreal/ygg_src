# Example Data

This directory contains example data files to help you get started with the Exercise Tracker.

## What's Included

### exercises.csv

Contains 10 sample exercises covering major movement patterns:

**Compound Movements** (with warmups):
1. Barbell Back Squat (rep range 8-12)
2. Barbell Bench Press (linear weight, 5 reps)
3. Deadlift (linear weight, 5 reps)
4. Overhead Press (linear weight, 5 reps)
5. Barbell Rows (rep range 8-12)
6. Romanian Deadlift (rep range 8-12)

**Accessory Movements** (no warmups):
7. Lat Pulldowns (rep range 10-15)
8. Dumbbell Bicep Curls (rep range 10-15)
9. Leg Press (rep range 10-15)
10. Face Pulls (rep range 12-20)

### workouts.csv

Contains 3 sample workout templates:

1. **Push Day A**: Bench Press, Overhead Press, Bicep Curls
2. **Pull Day A**: Deadlift, Barbell Rows, Lat Pulldowns, Face Pulls
3. **Leg Day A**: Barbell Squat, Leg Press, Romanian Deadlift

## How to Use

### Option 1: Start Fresh with Example Data

If you haven't started using the app yet:

```bash
# From the exercise_module directory
cp examples/*.csv data/
```

This will populate your app with example exercises and workouts.

### Option 2: Add to Existing Data

If you already have some data and want to add examples:

**Warning**: This may cause ID conflicts. Better to manually create exercises in the app.

1. Open `examples/exercises.csv` in a text editor
2. View the exercise configurations
3. Manually create similar exercises in the Exercise Library page
4. Create workouts using your newly created exercises

### Option 3: Reference Only

Use the example files as a reference for:
- Understanding CSV file format
- Seeing proper warmup configuration JSON structure
- Getting ideas for exercise configurations
- Understanding progression scheme differences

## Example Exercise Configurations

### Rep Range Progression (Hypertrophy Focus)

```
Exercise: Barbell Back Squat
Scheme: rep_range
Range: 8-12 reps
Increment: 5 lbs
Warmups: Enabled (intensity-based, 1-3 sets)
```

Progression: 135×8 → 135×9 → ... → 135×12 → 140×8 → ...

### Linear Weight Progression (Strength Focus)

```
Exercise: Barbell Bench Press
Scheme: linear_weight
Target: 5 reps (constant)
Increment: 5 lbs
Warmups: Enabled (2-3 sets based on intensity)
```

Progression: 135×5 → 140×5 → 145×5 → ...

### Isolation Exercise (No Warmup)

```
Exercise: Dumbbell Bicep Curls
Scheme: rep_range
Range: 10-15 reps
Increment: 2.5 lbs
Warmups: Disabled
```

Progression: 20×10 → 20×11 → ... → 20×15 → 22.5×10 → ...

## Warmup Configuration Format

Example warmup config JSON (for reference):

```json
{
  "enabled": true,
  "intensity_thresholds": [
    {"min_percent_1rm": 0, "max_percent_1rm": 50, "warmup_sets": 1},
    {"min_percent_1rm": 50, "max_percent_1rm": 70, "warmup_sets": 2},
    {"min_percent_1rm": 70, "max_percent_1rm": 100, "warmup_sets": 3}
  ],
  "warmup_percentages": [40, 60, 80],
  "warmup_reps": [8, 6, 4]
}
```

**Explanation**:
- Working at 0-50% of 1RM: 1 warmup set
- Working at 50-70% of 1RM: 2 warmup sets
- Working at 70-100% of 1RM: 3 warmup sets
- Warmup weights: 40%, 60%, 80% of working weight
- Warmup reps: 8, 6, 4 reps respectively

## Important Notes

### ID Conflicts

If you copy the example CSV files to your `data/` directory after already creating exercises/workouts:
- IDs may conflict (e.g., you might already have an exercise with ID 1)
- This can cause unexpected behavior
- Better to start fresh or manually create exercises

### Starting Weights

All exercises in the example start at the default weight (45 lbs):
- On first workout, use "Adjust Weight/Reps" to set appropriate starting weight
- Future workouts will progress from that weight

### Customization

Feel free to modify the example files:
- Change rep ranges to suit your goals
- Adjust weight increments (smaller for upper body, larger for lower body)
- Modify warmup configurations
- Add your own exercises

## CSV Format Notes

### Required Columns

All columns in the schema must be present, but some can be empty:

- **description**: Can be empty
- **secondary_muscle_groups**: Can be empty
- **rep_range_min/max**: Empty for linear_weight scheme
- **target_reps**: Empty for rep_range scheme
- **warmup_config**: Empty/null if warmups disabled

### Comma Handling

- Muscle groups: Comma-separated within the field (e.g., "Quadriceps,Glutes")
- Exercise IDs in workouts: Comma-separated (e.g., "1,2,3")
- JSON fields: Commas within JSON are part of the JSON structure

### Date Format

All dates in format: `YYYY-MM-DD HH:MM:SS`

Example: `2025-11-01 10:00:00`

## Next Steps

After loading example data:

1. Navigate to **Exercise Library** to see all exercises
2. Navigate to **Create Workout** to see how workouts are structured
3. Go to **Workout Overview** and start one of the example workouts
4. Execute a workout to see progression logic in action

## Need Help?

See the main documentation:
- [README.md](library/software/external_libraries/agent-os/agent-os-sandbox/exercise_module/README.md) - Full usage guide
- [QUICKSTART.md](library/software/external_libraries/agent-os/agent-os-sandbox/exercise_module/QUICKSTART.md) - Quick start guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
