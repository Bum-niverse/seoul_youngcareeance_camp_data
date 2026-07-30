# Seoul Bank Marketing Analysis

Exploratory data analysis completed for the DATA_B assignment of the Seoul Young Career Experience Camp.

The project analyzes a bank term-deposit marketing dataset to identify customer groups with higher historical subscription rates and to propose more efficient contact strategies.

## Dataset

- 41,188 records
- 21 variables
- Customer demographics and financial status
- Current and previous campaign activity
- Macroeconomic indicators

## Analysis Workflow

1. Audited duplicate rows, unknown categories, and special values.
2. Excluded call duration from pre-contact targeting to prevent data leakage.
3. Compared subscription rates across customer, financial, campaign, and economic variables.
4. Built a non-overlapping targeting rule using prior campaign outcomes, age, and occupation.
5. Evaluated the rule with selection rate, subscription rate, lift, and subscriber capture.

## Key Historical Result

The final rule selected 2,662 customers, or 6.46% of the dataset. Within the historical data, this group had a 48.69% subscription rate, a 4.32× lift over the overall average, and contained 27.93% of all subscribers.

These figures describe associations in the supplied dataset; they are not causal claims or guaranteed future performance.

## Repository Structure

- `analysis/`: analysis code and notebooks
- `data/`: source or prepared data files permitted for repository use
- `docs/`: supporting notes and outputs
- `requirements.txt`: Python dependencies

## Run Locally

```bash
python -m venv .venv
pip install -r requirements.txt
```

Then run the analysis files in `analysis/` in their documented order.

