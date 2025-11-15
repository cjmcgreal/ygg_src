# Known Issues

## Integration Test Failures

### Issue 1: Failure Handling Not Working as Expected
**Test:** `test_failure_handling_repeats_parameters`
**Status:** Bug in implementation
**Description:** When a workout is partially completed (e.g., only 2 out of 3 sets), the progression logic still treats it as successful and progresses to the next weight. The `is_workout_successful()` function only checks if completed sets hit target reps, but doesn't verify that ALL prescribed sets were completed.

**Expected Behavior:**
- Workout 1: 45 lbs x 5 reps (all 3 sets) - Success
- Workout 2: 50 lbs x 5 reps (only 2 out of 3 sets) - Failure
- Workout 3: Should repeat 50 lbs x 5 reps (no progression)

**Actual Behavior:**
- Workout 3: Progresses to 55 lbs x 5 reps

**Root Cause:** `is_workout_successful()` in `logic.py` only checks completed sets but doesn't count whether the total number of completed working sets matches the expected number (3 sets).

**Impact:** Medium - Users who fail to complete all sets will progress anyway, potentially leading to overtraining or injury.

**Suggested Fix:** Modify `is_workout_successful()` to also check that the total number of completed working sets equals the expected number (currently hardcoded to 3).

### Issue 2: Workout Duration Calculation is Zero
**Test:** `test_metadata_calculation_at_all_three_levels`
**Status:** Bug in implementation
**Description:** When workout metadata is calculated, the `duration_seconds` field is 0 even though sets have timestamps.

**Expected Behavior:** `duration_seconds` should be calculated as `end_time - start_time` where end_time is when the workout was completed.

**Actual Behavior:** `duration_seconds` is 0.

**Root Cause:** Need to investigate `calculate_workout_metadata()` in `analysis.py` and `handle_complete_workout()` in `workflow.py` to see how duration is calculated.

**Impact:** Low - Duration tracking is not critical for progression logic but is useful for analytics.

**Suggested Fix:** Ensure `end_time` is properly set and `calculate_workout_metadata()` correctly calculates the difference.

## MVP Limitations

These are intentional limitations of the MVP, not bugs:

1. **No Exercise Edit/Delete:** Once created, exercises cannot be modified or deleted
2. **No Workout Template Edit/Delete:** Workout templates are immutable
3. **Fixed 3 Working Sets:** All exercises have exactly 3 working sets (hardcoded)
4. **No Rest Timer:** Rest times are displayed but not actively counted down
5. **No Plate Calculator:** Users must calculate barbell loading themselves
6. **Fixed Starting Weight:** All exercises start at 45 lbs (bar weight) regardless of user strength
7. **No Deload Logic:** No automatic deload after multiple failures
8. **Simple Failure Detection:** Only checks if all sets completed, not rep targets per set

## Future Enhancements

1. Fix failure handling to properly detect incomplete workouts
2. Fix duration calculation
3. Add configurable starting weights per exercise
4. Add configurable number of working sets per exercise
5. Implement automatic deload after 3 consecutive failures
6. Add edit/delete functionality for exercises and workouts
