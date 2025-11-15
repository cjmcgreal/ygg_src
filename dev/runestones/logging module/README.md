# Runestones Framework Monitor

A comprehensive monitoring dashboard for tracking LLM job executions, token usage, and project metrics in the Runestones framework.

## Features

- **Dashboard Overview**: View key metrics including total jobs, tokens, tasks, and costs
- **Project Management**: Monitor individual projects with detailed metrics and budget tracking
- **Job Tracking**: Track individual LLM job executions with filtering and efficiency analysis
- **Model Comparison**: Compare performance and costs across different LLM models
- **Data Entry**: Add new projects and jobs through interactive forms
- **Visualizations**: Interactive charts and graphs powered by Plotly

## Project Structure

```
logging module/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── src/
│   └── runestones/
│       ├── runestones_app.py      # Streamlit UI layer
│       ├── runestones_workflow.py # API interface/orchestration layer
│       ├── runestones_logic.py    # Business logic and validation
│       ├── runestones_analysis.py # Data analysis and metrics
│       ├── runestones_db.py       # CSV database interface
│       └── runestones_data/       # CSV data files
│           ├── projects.csv       # Project metadata
│           ├── jobs.csv           # Job execution records
│           └── job_metrics.csv    # Token and task metrics
└── tests/
    └── runestones/
        ├── test_runestones_db.py
        ├── test_runestones_logic.py
        ├── test_runestones_analysis.py
        └── test_runestones_workflow.py
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Dashboard

Start the Streamlit application:
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run tests for a specific module:
```bash
pytest tests/runestones/test_runestones_db.py -v
```

### Testing Individual Modules

Each module can be run standalone to see example usage:

```bash
# Test database layer
python src/runestones/runestones_db.py

# Test analysis layer
python src/runestones/runestones_analysis.py

# Test logic layer
python src/runestones/runestones_logic.py

# Test workflow layer
python src/runestones/runestones_workflow.py
```

## Data Model

### Projects (projects.csv)
- `project_id`: Unique project identifier
- `project_name`: Name of the project
- `description`: Project description
- `created_date`: Date the project was created

### Jobs (jobs.csv)
- `job_id`: Unique job identifier
- `project_id`: Associated project ID
- `prompt_text`: The prompt sent to the LLM
- `llm_model`: The LLM model used (e.g., gpt-4, claude-3-opus)
- `status`: Job status (pending, in_progress, completed, failed)
- `created_date`: When the job was created
- `completed_date`: When the job was completed

### Job Metrics (job_metrics.csv)
- `job_id`: Associated job ID
- `token_count`: Total tokens used
- `task_count`: Number of tasks in the job
- `input_tokens`: Input token count
- `output_tokens`: Output token count
- `total_cost`: Total cost in dollars

## Architecture

The application follows a clean layered architecture:

1. **UI Layer** (`runestones_app.py`): Streamlit interface with visualizations
2. **Workflow Layer** (`runestones_workflow.py`): Orchestrates business operations
3. **Logic Layer** (`runestones_logic.py`): Business rules and validation
4. **Analysis Layer** (`runestones_analysis.py`): Data analysis and metrics
5. **Database Layer** (`runestones_db.py`): CSV file operations

## Key Features

### Dashboard Tab
- Overall statistics (jobs, tokens, tasks, costs)
- Job status distribution pie chart
- Top projects by token usage and cost
- Model usage statistics

### Projects Tab
- View all projects with job counts
- Detailed project view with metrics
- Budget tracking and alerts
- Jobs list per project

### Jobs Tab
- Filter jobs by status and project
- Job efficiency analysis
- Visualization of tasks vs tokens
- Detailed job information

### Models Tab
- Compare LLM models by usage
- Token and cost analysis per model
- Average metrics comparison

### Add Data Tab
- Create new projects with validation
- Add new jobs with automatic cost calculation
- Form validation and error handling

## Business Rules

- **Token Pricing** (per 1K tokens):
  - GPT-4: $0.06
  - GPT-3.5-turbo: $0.002
  - Claude-3-opus: $0.075
  - Claude-3-sonnet: $0.015
  - Claude-3-haiku: $0.0025

- **Job Priority**:
  - HIGH: 10+ tasks or "urgent/critical" in project name
  - MEDIUM: 5-9 tasks
  - LOW: <5 tasks

- **Budget Limit**: Default $100 per project

- **Efficiency Score**: Tasks per 1000 tokens

## Adding Integration with Runestones Framework

To integrate with your actual Runestones framework:

1. **Logging Jobs**: After each LLM call, add job data:
```python
import runestones_workflow as workflow

# When a job starts
job_id = workflow.create_new_job(
    project_id=1,
    prompt_text="Your prompt here",
    llm_model="gpt-4",
    token_count=2500,
    task_count=3,
    input_tokens=500,
    output_tokens=2000
)
```

2. **Updating Job Status**:
```python
workflow.update_job_status_workflow(job_id, 'completed')
```

3. **Batch Import**: Create a script to import existing logs into the CSV files

## Future Enhancements

- Time series analysis of job creation
- Export reports to PDF
- API endpoint for programmatic access
- Real-time job monitoring
- Advanced filtering and search
- Cost forecasting and trends
- Integration with CI/CD pipelines

## Contributing

When adding new features, follow the layered architecture:
1. Add data operations to `runestones_db.py`
2. Add analysis functions to `runestones_analysis.py`
3. Add business logic to `runestones_logic.py`
4. Add orchestration to `runestones_workflow.py`
5. Add UI to `runestones_app.py`
6. Add tests for each layer

## License

MIT License
