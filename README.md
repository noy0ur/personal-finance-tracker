# Personal Finance Tracker Dashboard

A beginner-friendly Python web app for recording income and expenses, viewing spending patterns, and comparing monthly expenses against a budget.

## Features
- Add income and expense transactions
- Import transaction data from a CSV file
- Monthly income, expenses, net balance, and savings-rate summary
- Expense breakdown by category
- Monthly income-versus-expense chart
- Monthly budget progress and overspending alert
- Filter transaction records and download data as CSV

## Run locally

Python 3.10 or newer is recommended.

```bash
pip install -r requirements.txt
streamlit run app.py
```

## CSV format

The imported CSV must include these columns:

| date | type | category | description | amount |
|---|---|---|---|---:|
| 2026-01-01 | Income | Salary | Monthly salary | 45000 |
| 2026-01-02 | Expense | Food | Groceries | 1200 |

- `date`: a date such as `2026-01-01`
- `type`: `Income` or `Expense`
- `category`: category name
- `description`: short text
- `amount`: positive numeric amount; use positive values for both income and expenses

The app includes `sample_transactions.csv` for testing.

## Deploy using Streamlit Community Cloud

1. Upload the project files to a GitHub repository.
2. Open https://share.streamlit.io/
3. Select **Create app** and choose your repository.
4. Set the main file path to `app.py`.
5. Deploy.

## Tech stack
Python, Streamlit, Pandas, Plotly, CSV data validation, and Git/GitHub.

## Limitations and privacy
This is a portfolio demo, not a banking application. Data entered in the app is held in the current session unless exported. Do not upload real bank statements or sensitive financial records to a public GitHub repository. For a production app, add authentication, persistent storage, testing, and security controls.

## Suggested future improvements
- SQLite database for persistent transactions
- Edit/delete transaction controls
- Category-specific budgets
- Automated unit tests and GitHub Actions
- Monthly PDF report export
