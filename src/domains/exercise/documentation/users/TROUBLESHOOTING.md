# Troubleshooting Guide

This guide covers common issues and their solutions for the Exercise Tracker application.

## Installation Issues

### Issue: "Python not found" or "python3: command not found"

**Problem**: Python is not installed or not in your PATH.

**Solution**:
1. Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
2. During installation, make sure to check "Add Python to PATH"
3. Verify installation:
   ```bash
   python3 --version
   ```

### Issue: "pip: command not found"

**Problem**: pip is not installed or not in your PATH.

**Solution**:
1. pip usually comes with Python. Try:
   ```bash
   python3 -m pip --version
   ```
2. If still not found, install pip:
   ```bash
   python3 -m ensurepip --default-pip
   ```

### Issue: Dependencies fail to install

**Problem**: Some packages fail during `pip install -r requirements.txt`

**Solution**:
1. Upgrade pip:
   ```bash
   python3 -m pip install --upgrade pip
   ```
2. Try installing dependencies individually:
   ```bash
   pip install streamlit
   pip install pandas
   pip install pytest
   ```
3. Check Python version (must be 3.8+):
   ```bash
   python3 --version
   ```

### Issue: Virtual environment activation fails on Windows

**Problem**: `venv\Scripts\activate` doesn't work

**Solution**:
1. Use PowerShell instead of Command Prompt
2. Or try:
   ```powershell
   venv\Scripts\Activate.ps1
   ```
3. If execution policy error, run PowerShell as Administrator:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## Application Startup Issues

### Issue: "streamlit: command not found"

**Problem**: Streamlit not installed or virtual environment not activated.

**Solution**:
1. Verify virtual environment is activated (you should see `(venv)` in terminal)
2. If not activated:
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Verify Streamlit is installed:
   ```bash
   pip list | grep streamlit
   ```

### Issue: Application starts but shows blank page

**Problem**: Browser cache or Streamlit configuration issue.

**Solution**:
1. Hard refresh browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Try different browser
4. Check terminal for error messages

### Issue: Port already in use

**Problem**: Another application is using port 8501.

**Solution**:
1. Kill existing Streamlit process
2. Or run on different port:
   ```bash
   streamlit run app.py --server.port 8502
   ```

## Data Issues

### Issue: "FileNotFoundError" or "CSV file not found"

**Problem**: Data directory or CSV files missing.

**Solution**:
The app creates the `data/` directory and CSV files automatically on first use. If you see this error:

1. Ensure you're running from the correct directory:
   ```bash
   pwd  # Should show /path/to/exercise_module
   ```
2. Check if data directory exists:
   ```bash
   ls -la data/
   ```
3. If missing, create it:
   ```bash
   mkdir data
   ```
4. Restart the application

### Issue: "Datetime parsing error" or "Invalid date format"

**Problem**: CSV file has corrupted datetime data.

**Solution**:
1. Check CSV file for invalid dates
2. Dates should be in format: `YYYY-MM-DD HH:MM:SS`
3. If file is corrupted, delete it (data will be lost):
   ```bash
   rm data/workout_logs.csv
   ```
4. Or backup and reset:
   ```bash
   mv data data_backup
   mkdir data
   ```

### Issue: Data not saving or changes not persisting

**Problem**: File permissions or disk space issue.

**Solution**:
1. Check file permissions:
   ```bash
   ls -la data/
   ```
   Files should be writable by your user.

2. Check disk space:
   ```bash
   df -h .
   ```

3. Verify CSV files are being updated:
   ```bash
   ls -lh data/
   ```
   Check timestamps after making changes.

### Issue: CSV data appears corrupted or unreadable

**Problem**: Data was manually edited incorrectly or file encoding issue.

**Solution**:
1. Open CSV file in text editor (not Excel)
2. Check for:
   - Proper comma separation
   - Matching number of columns in all rows
   - No extra commas in data fields
   - Proper quote escaping

3. If unfixable, restore from backup or reset:
   ```bash
   rm data/corrupted_file.csv
   ```

## Session State Issues

### Issue: Session state not persisting during workout

**Problem**: Completed sets disappear or progress resets.

**Solution**:
1. Don't refresh browser during workout
2. Don't navigate away and back to execution page
3. Browser storage might be disabled - check browser settings
4. Try different browser

### Issue: "Workout not found" after clicking Start Workout

**Problem**: workout_id not stored in session state.

**Solution**:
1. Return to Workout Overview page
2. Click "Start Workout" again
3. Don't manually navigate to workout execution page
4. If persists, restart application

### Issue: Cannot complete workout - button disabled

**Problem**: Not all required working sets are marked complete.

**Solution**:
1. Check all working sets have checkboxes marked
2. Warmup sets are optional - only working sets required
3. Ensure at least one set per exercise is completed
4. Check for error messages in terminal

## Progression Issues

### Issue: Workout not progressing despite completing all sets

**Problem**: This is a known issue (see KNOWN_ISSUES.md).

**Current behavior**: If you don't complete ALL prescribed sets (e.g., only 2 out of 3), the workout may still progress.

**Workaround**: Always complete all 3 working sets to ensure proper progression tracking.

### Issue: Starting weight is too heavy/light

**Problem**: Default starting weight is 45 lbs (barbell) for all exercises.

**Workaround**:
1. For first workout, use "Adjust Weight/Reps" to override target weight
2. Enter appropriate starting weight for your strength level
3. Future workouts will progress from that weight

### Issue: Warmup sets not generating

**Problem**: Warmup config not enabled or no 1RM history.

**Solution**:
1. Check exercise has warmup enabled:
   - Go to Exercise Library
   - View exercise details
   - Warmup config should be present

2. If first time doing exercise, no warmup will generate (no 1RM estimate yet)
3. After first workout, warmups will generate based on 1RM

### Issue: Incorrect 1RM estimate

**Problem**: 1RM calculation seems wrong.

**Explanation**:
- Uses Epley formula: 1RM = weight × (1 + reps/30)
- Most accurate for 3-10 rep range
- Less accurate for very high or very low reps

**Solution**:
- Don't rely on 1RM estimate for sets outside 3-10 rep range
- 1RM is used for warmup generation, not for setting working weights directly
- Working weights are determined by progression logic, not 1RM

## Performance Issues

### Issue: Application is slow to load

**Problem**: Large CSV files or slow disk.

**Solution**:
1. Check CSV file sizes:
   ```bash
   ls -lh data/
   ```
2. If files are very large (>100MB), consider:
   - Archiving old data
   - Starting fresh with new data files

### Issue: Workout execution page is slow

**Problem**: Complex calculations or many exercises.

**Solution**:
1. Reduce number of exercises in workout
2. This is expected for workouts with 10+ exercises
3. Consider splitting into multiple smaller workouts

## Backup and Recovery

### How to backup your data

**Option 1: Manual backup**
```bash
cp -r data/ data_backup_$(date +%Y%m%d)
```

**Option 2: Regular backups**
Set up a cron job (Linux/Mac) or scheduled task (Windows) to backup daily.

### How to restore from backup

```bash
# Rename current data (just in case)
mv data/ data_old

# Restore from backup
cp -r data_backup_YYYYMMDD/ data/
```

### How to reset all data (start fresh)

**Warning**: This deletes all your workout history!

```bash
# Backup first (just in case)
cp -r data/ data_backup

# Delete all data
rm data/*.csv

# Or delete entire data directory
rm -rf data/
mkdir data
```

Restart the application. It will create fresh CSV files.

### How to export data

All data is already in CSV format. To export:

1. Copy the `data/` directory to desired location
2. CSV files can be opened in Excel, Google Sheets, or any spreadsheet application
3. For analysis, use Python pandas:
   ```python
   import pandas as pd
   workouts = pd.read_csv('data/workout_logs.csv')
   ```

## Browser-Specific Issues

### Chrome

**Issue**: Application won't load after update
- Clear cache: Settings → Privacy and security → Clear browsing data
- Disable extensions and try again

### Firefox

**Issue**: Session state not persisting
- Check if cookies are enabled
- Privacy settings may block local storage

### Safari

**Issue**: Styling looks wrong
- Safari may not support all Streamlit features
- Try Chrome or Firefox instead

## Development Issues

### Issue: Tests failing

**Problem**: Test suite has known failures.

**Solution**:
1. Check KNOWN_ISSUES.md for documented test failures
2. Run specific test to isolate issue:
   ```bash
   pytest tests/test_logic.py::test_specific_function -v
   ```
3. Some test failures are documented and expected in MVP

### Issue: Import errors when running tests

**Problem**: Module not found errors.

**Solution**:
1. Ensure you're in the project root directory
2. Install package in editable mode:
   ```bash
   pip install -e .
   ```
3. Or add to PYTHONPATH:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

## Getting Help

If your issue isn't covered here:

1. Check [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for documented limitations
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
3. Review terminal output for error messages
4. Check browser console for JavaScript errors (F12 → Console)
5. Try the [QUICKSTART.md](library/software/external_libraries/agent-os/agent-os-sandbox/exercise_module/QUICKSTART.md) guide for a fresh setup

## Error Messages Explained

### "ValueError: Exercise name is required"

**Cause**: Tried to create exercise with empty name.

**Solution**: Enter a name before clicking "Create Exercise".

### "ValueError: At least one primary muscle group is required"

**Cause**: No primary muscle groups selected.

**Solution**: Select at least one muscle group from the list.

### "ValueError: Workout name required"

**Cause**: Tried to create workout with empty name.

**Solution**: Enter a workout name.

### "ValueError: At least one exercise required"

**Cause**: Tried to create workout without selecting exercises.

**Solution**: Select at least one exercise from the list.

### "KeyError: 'workout_id'"

**Cause**: Tried to access workout execution page without starting a workout.

**Solution**: Go to Workout Overview page and click "Start Workout" first.

### "pandas.errors.EmptyDataError"

**Cause**: CSV file exists but is completely empty.

**Solution**: Delete the empty CSV file and restart the application.

## Common Questions

### Q: Can I edit exercises after creating them?

**A**: Not in the current MVP. See KNOWN_ISSUES.md for limitations. You would need to manually edit the CSV file.

### Q: Can I delete workouts?

**A**: Not in the current MVP. See KNOWN_ISSUES.md for limitations.

### Q: How do I change the number of working sets?

**A**: Currently hardcoded to 3 sets. See KNOWN_ISSUES.md for limitations.

### Q: Can I use kilograms instead of pounds?

**A**: The app doesn't enforce units. Just use kg consistently for all weights.

### Q: How accurate is the calorie calculation?

**A**: Moderately accurate. Uses MET formula with fixed MET value of 5.0. Actual calories vary based on intensity and individual metabolism.

### Q: Why does my workout duration show 0 seconds?

**A**: This is a known bug. See KNOWN_ISSUES.md issue #2.

### Q: Can multiple people use this app?

**A**: No, it's designed for single-user, local installation. All data is stored locally.

### Q: Can I sync data between devices?

**A**: Not currently. You could manually copy the `data/` directory, but there's no automatic sync.

## Still Having Issues?

Create a GitHub issue with:
1. Description of the problem
2. Steps to reproduce
3. Error messages (terminal and browser console)
4. Operating system and Python version
5. Contents of requirements.txt that you installed
