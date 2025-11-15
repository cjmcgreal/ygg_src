# Financial Dashboard Prototype - 5 Frontend Styles

A Streamlit-based prototype showcasing 5 different frontend styles for displaying time series financial data. All styles work with the same underlying dataset of 100 mock financial transactions.

## Features

### 5 Distinct Frontend Styles:

1. **Executive Dashboard** - High-level KPI cards and executive summary charts
2. **Data Table Focus** - Interactive tables with advanced filtering and sorting
3. **Analytics Lab** - Advanced visualizations and statistical deep-dives
4. **Minimalist View** - Clean, simple interface with essential information
5. **Timeline Explorer** - Chronological navigation with timeline visualizations

Each style behaves like a standalone app with its own tabs and features, all accessible through a sidebar selector.

## Installation

```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
.
├── app.py                          # Main entry point with sidebar selector
├── requirements.txt
├── src/
│   ├── shared/                     # Shared data and analysis functions
│   │   ├── shared_db.py           # CSV database interface
│   │   ├── shared_analysis.py     # Data analysis functions
│   │   └── shared_data/           # CSV data files
│   │       └── transactions.csv
│   ├── executive/                  # Style 1: Executive Dashboard
│   │   └── executive_app.py
│   ├── datatable/                  # Style 2: Data Table Focus
│   │   └── datatable_app.py
│   ├── analytics/                  # Style 3: Analytics Lab
│   │   └── analytics_app.py
│   ├── minimalist/                 # Style 4: Minimalist View
│   │   └── minimalist_app.py
│   └── timeline/                   # Style 5: Timeline Explorer
│       └── timeline_app.py
└── tests/                          # Test directory structure
```

## Dataset

The prototype uses a mock dataset of 100 financial transactions including:
- Date range: Past 6 months
- Transaction types: Income (20%) and Expenses (80%)
- Multiple categories: Salary, Freelance, Groceries, Dining, Rent, etc.
- Amount range: $10 - $5000

The dataset is automatically generated on first run and stored in `src/shared/shared_data/transactions.csv`

## Usage

1. **Select a Style**: Use the sidebar radio buttons to choose from 5 different frontend styles
2. **Explore the Data**: Each style has multiple tabs with different views and visualizations
3. **Compare Styles**: Switch between styles to see different approaches to displaying the same data

## Style Details

### Executive Dashboard
- KPI metric cards
- Monthly income vs expenses charts
- Category pie charts
- Performance metrics grid

### Data Table Focus
- Advanced filtering by date, category, type, and amount
- Separate views for income, expenses, and all transactions
- Category summary analysis
- CSV export functionality

### Analytics Lab
- Time series analysis with moving averages
- Distribution histograms and box plots
- Correlation heatmaps
- Day-of-week pattern analysis
- Statistical deep dives

### Minimalist View
- Clean, uncluttered design
- Essential metrics only
- Simple balance trends
- Recent transactions list

### Timeline Explorer
- Interactive scatter timeline
- Calendar heatmap views
- Weekly breakdowns
- Chronological event stream
- Annotated balance timeline

## Development

Each style is completely independent and can be run standalone:

```bash
streamlit run src/executive/executive_app.py
streamlit run src/datatable/datatable_app.py
streamlit run src/analytics/analytics_app.py
streamlit run src/minimalist/minimalist_app.py
streamlit run src/timeline/timeline_app.py
```

## Technologies

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computing
