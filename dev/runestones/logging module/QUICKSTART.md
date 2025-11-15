# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 3. Explore the Dashboard

### Dashboard Tab
- View overall statistics (jobs, tokens, costs)
- See job status distribution
- View top projects by token usage and cost
- Compare LLM model usage

### Projects Tab
- Browse all projects
- Select a project to view detailed metrics
- Track project budget status
- View all jobs within a project

### Jobs Tab
- View all jobs with filtering options
- Filter by status (completed, in_progress, pending)
- Filter by project
- Analyze job efficiency

### Models Tab
- Compare different LLM models
- View token usage and costs per model
- Analyze average metrics

### Add Data Tab
- Create new projects
- Add new jobs with automatic cost calculation
- Form validation ensures data quality

## 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/runestones/test_runestones_db.py -v

# Run with coverage
pytest tests/ --cov=src/runestones --cov-report=html
```

## 5. Test Individual Modules

Each module has a standalone test section:

```bash
# Test database operations
python src/runestones/runestones_db.py

# Test analysis functions
python src/runestones/runestones_analysis.py

# Test business logic
python src/runestones/runestones_logic.py

# Test workflow orchestration
cd src/runestones && python runestones_workflow.py
```

## 6. Sample Data

The system comes with sample data in `src/runestones/runestones_data/`:
- 3 projects (Content Generation, Code Review Assistant, Data Analysis)
- 7+ sample jobs with various statuses
- Complete metrics for each job

## 7. Adding Your Own Data

### Via the Dashboard
Use the "Add Data" tab to create projects and jobs through the web interface.

### Programmatically
```python
import sys
sys.path.append('src/runestones')
import runestones_workflow as workflow

# Create a project
success, message, project_id = workflow.create_new_project(
    "My New Project",
    "Description here"
)

# Create a job
success, message, job_id = workflow.create_new_job(
    project_id=project_id,
    prompt_text="Your prompt here",
    llm_model="gpt-4",
    token_count=2500,
    task_count=3,
    input_tokens=500,
    output_tokens=2000
)
```

### Direct CSV Editing
You can also directly edit the CSV files in `src/runestones/runestones_data/`:
- `projects.csv` - Add new projects
- `jobs.csv` - Add new jobs
- `job_metrics.csv` - Add job metrics

## 8. Integration with Runestones Framework

To log jobs from your Runestones framework:

```python
# In your Runestones framework code
import runestones_workflow as workflow

def run_llm_job(project_id, prompt, model):
    # Your existing LLM execution code
    response = call_llm(prompt, model)

    # Log the job to the monitoring system
    workflow.create_new_job(
        project_id=project_id,
        prompt_text=prompt,
        llm_model=model,
        token_count=response.total_tokens,
        task_count=count_tasks(response),
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens
    )

    return response
```

## 9. Key Metrics Explained

- **Token Count**: Total tokens used (input + output)
- **Task Count**: Number of tasks in the job
- **Efficiency Score**: Tasks per 1000 tokens (higher is better)
- **Cost**: Calculated based on model pricing
- **Budget Status**: Compares project cost against budget limit

## 10. Troubleshooting

### Dashboard won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ recommended)

### Tests failing
- Ensure you're in the project root directory
- Check that CSV files exist in `src/runestones/runestones_data/`

### Import errors
- Verify the directory structure matches the documented layout
- Check that `__pycache__` directories aren't corrupted

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the architecture and layer responsibilities
- Integrate with your actual Runestones framework
- Customize the visualizations for your needs
- Add additional metrics or analysis functions

---

**Need Help?** Check the README.md for more detailed information about the architecture, data model, and customization options.
