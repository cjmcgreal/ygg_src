# Quick Start Guide

## Installation & Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

3. Open your browser to `http://localhost:8501`

## Using the App

### Sidebar Navigation
- Use the radio buttons in the sidebar to select from 5 different frontend styles
- Each style displays the same underlying dataset in a different way
- Style descriptions are shown in the sidebar

### The 5 Styles

**1. Executive Dashboard**
- Best for: Quick overview and management reporting
- Features: KPI cards, monthly trends, category breakdowns
- Tabs: Monthly Trends | Category Breakdown | Performance Metrics

**2. Data Table Focus**
- Best for: Detailed data exploration and filtering
- Features: Advanced filters, sortable tables, CSV export
- Tabs: All Transactions | Income Only | Expenses Only | Category Summary

**3. Analytics Lab**
- Best for: Deep statistical analysis
- Features: Time series analysis, distributions, correlations, heatmaps
- Tabs: Time Series | Distribution | Correlation & Patterns | Comparative | Statistics

**4. Minimalist View**
- Best for: Clean, distraction-free overview
- Features: Essential metrics only, simple charts
- Tabs: Summary | Trends | Details

**5. Timeline Explorer**
- Best for: Chronological analysis and event tracking
- Features: Interactive timeline, calendar heatmap, weekly breakdowns
- Tabs: Interactive Timeline | Calendar View | Weekly Breakdown | Event Stream

## Dataset

The app uses a mock dataset of 100 financial transactions:
- **Time period**: Past 6 months
- **Types**: Income (20%), Expenses (80%)
- **Categories**: Salary, Freelance, Groceries, Dining, Rent, Utilities, etc.
- **Amount range**: $10 - $5,000

The data is automatically generated on first run and saved to:
`src/shared/shared_data/transactions.csv`

## Tips

- Each style behaves like a standalone app with its own navigation
- All styles share the same data, so you can compare approaches
- Try switching between styles to see different perspectives on the same data
- The Data Table Focus style lets you export filtered data as CSV
- The Analytics Lab has the most detailed visualizations
- The Minimalist View is great for presentations

## Running Individual Styles

You can also run each style standalone for testing:

```bash
streamlit run src/executive/executive_app.py
streamlit run src/datatable/datatable_app.py
streamlit run src/analytics/analytics_app.py
streamlit run src/minimalist/minimalist_app.py
streamlit run src/timeline/timeline_app.py
```

## Customization

To use your own data:
1. Replace `src/shared/shared_data/transactions.csv` with your data
2. Ensure it has these columns: `transaction_id`, `date`, `amount`, `category`, `description`, `type`
3. Restart the app

Enjoy exploring the different frontend styles!
