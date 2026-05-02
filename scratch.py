#%%
import pandas as pd
d = pd.read_csv('enriched_grok_df.csv')

#%%
# Get all columns that start with 'app_'
app_columns = [col for col in d.columns if col.startswith('app_')]

# Group by field_office_slug and sum the app_ columns
result = d.groupby('field_office_slug')[app_columns].sum()

# Add row count column
result['row_count'] = d.groupby('field_office_slug').size()

result

# %%
