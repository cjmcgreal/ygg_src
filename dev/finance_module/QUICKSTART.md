# Finance Dashboard - Quick Start Guide

## 🚀 Getting Started (5 minutes)

### 1. Start the Application

```bash
cd finance_module
python src/finance/finance_app.py
```

Open your browser to: **http://127.0.0.1:8050/**

### 2. Import Sample Data

The app comes pre-loaded with:
- ✅ 13 categories (dining, transportation, shopping, income, entertainment)
- ✅ 17 auto-labeling rules

**Use the provided sample file:**
- File: `sample_import.csv` (in the finance_module folder)
- Contains 7 sample transactions

**To import:**
1. Click the **"Import Data"** tab
2. Click **"Select CSV File"**
3. Choose `sample_import.csv`
4. Ensure **"Auto-label transactions"** is checked
5. Click **"Import Transactions"**

You should see:
```
✓ Import Successful
Imported: 7 transactions
Duplicates skipped: 0
Auto-labeled: 7
```

### 3. View Dashboard

1. Click **"Overview"** tab
2. You'll see:
   - Total Income: $3,500.00
   - Total Expenses: $216.24
   - Net: $3,283.76
   - Transactions: 7

3. Charts will display:
   - Spending over time (line chart)
   - Category breakdown (pie chart)

### 4. Review Transactions

1. Click **"Review Transactions"** tab
2. Click **"Apply Filters"** to see all transactions
3. You'll see transactions with auto-assigned categories:
   - STARBUCKS → dining/coffee
   - UBER → transportation/rideshare
   - SHELL → transportation/car/gas
   - etc.

---

## 📄 CSV Format Requirements

Your CSV file must have these columns:

### Required Columns

| Column | Description | Example |
|--------|-------------|---------|
| `date` | Transaction date | `2025-01-15` |
| `description` | Transaction description | `STARBUCKS COFFEE` |
| `amount` | Amount (negative=expense, positive=income) | `-5.50` or `3500.00` |

### Optional Columns

| Column | Description | Example |
|--------|-------------|---------|
| `account` | Account name | `Chase Credit` |
| `original_category` | Bank's category | `Food & Dining` |

### Example CSV

```csv
date,description,amount,account
2025-01-15,STARBUCKS COFFEE,-5.50,Chase Credit
2025-01-16,UBER RIDE,-45.00,Chase Credit
2025-02-05,PAYCHECK DEPOSIT,3500.00,Chase Checking
```

### Important Notes

✅ **Date format:** Use `YYYY-MM-DD` (e.g., 2025-01-15)
✅ **Negative amounts:** Expenses should be negative (e.g., -5.50)
✅ **Positive amounts:** Income should be positive (e.g., 3500.00)
✅ **No commas in amounts:** Use `1500.00` not `1,500.00`

---

## 🏷️ Adding Your Own Categories

### Adding a Category

1. Go to **"Manage Categories"** tab
2. In "Add New Category" section:
   - **Category Path**: Use `/` for hierarchy
     - Root: `transportation`
     - Level 1: `transportation/car`
     - Level 2: `transportation/car/gas`
   - **Display Name**: Human-readable name
   - **Color**: Pick a color for charts
3. Click **"Add Category"**

### Category Hierarchy Examples

```
dining
├── dining/coffee
├── dining/restaurants
└── dining/groceries

transportation
├── transportation/car
│   ├── transportation/car/gas
│   ├── transportation/car/maintenance
│   └── transportation/car/insurance
└── transportation/rideshare

housing
├── housing/rent
├── housing/utilities
└── housing/maintenance
```

---

## 🔤 Adding Label Rules

Label rules automatically categorize transactions based on text matching.

### Adding a Rule

1. Go to **"Manage Categories"** tab
2. Scroll to "Label Rules" section
3. Fill in:
   - **Substring**: Text to search for (e.g., `starbucks`)
   - **Category Path**: Category to assign (e.g., `dining/coffee`)
   - **Priority**: Higher numbers checked first (default: 10)
   - **Case Sensitive**: Usually leave unchecked
4. Click **"Add Rule"**

### Rule Examples

| Substring | Category | Priority | Notes |
|-----------|----------|----------|-------|
| `starbucks` | `dining/coffee` | 15 | Specific match |
| `coffee` | `dining/coffee` | 5 | Generic match (lower priority) |
| `uber` | `transportation/rideshare` | 20 | High priority |
| `shell` | `transportation/car/gas` | 15 | Gas stations |
| `paycheck` | `income/salary` | 25 | Income |

### Priority Rules

- **Higher priority = checked first**
- If description is "STARBUCKS COFFEE":
  - Matches `starbucks` (priority 15) → assigns `dining/coffee`
  - Would also match `coffee` (priority 5), but `starbucks` is checked first

---

## 💡 Tips & Tricks

### Exporting Bank Data

Most banks allow CSV export:
- **Chase**: Go to Activity → Download → CSV
- **Bank of America**: Go to Accounts → Export Transactions → CSV
- **Citi**: Go to Transactions → Download → CSV

### Common Issues

**Problem:** Import fails with datetime error
**Solution:** Ensure date column is named `date` and format is `YYYY-MM-DD`

**Problem:** Transactions not auto-labeled
**Solution:** Check that label rules exist and are enabled

**Problem:** Categories don't show in charts
**Solution:** Ensure transactions have been imported and labeled

### Best Practices

1. **Start with broad categories** (dining, transportation, housing)
2. **Add subcategories as needed** (dining/coffee, dining/restaurants)
3. **Use high priority for specific rules** (e.g., "starbucks" = 15)
4. **Use low priority for generic rules** (e.g., "coffee" = 5)
5. **Review and approve labels** to lock them

---

## 🎯 Next Steps

Once you've imported sample data:

1. **Add your own categories** matching your spending patterns
2. **Create label rules** for your common merchants
3. **Import your real transaction data** from your bank
4. **Review and approve** the auto-assigned labels
5. **Analyze your spending** on the Overview tab!

---

## 🆘 Need Help?

- **Documentation**: See `README.md` for full documentation
- **Sample Data**: Use `sample_import.csv` to test
- **Test Suite**: Run `pytest tests/finance/ -v` to verify everything works

---

**Enjoy tracking your finances! 📊💰**
