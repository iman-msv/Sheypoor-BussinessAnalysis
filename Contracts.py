# Required modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Reading the data set
contracts = pd.read_excel('Data contracts.xlsx')

# First few rows 
print(contracts.head())
# It would be wise to change farsi columns into English, but becasue of time limit, I ignore this step.

# Data Types
print(contracts.info())

# contract_date, start_date, and end_date should be transformed into a datatime objects.
# Note: there are missing values in columns contract_date, start_date, and region.
# real_end_date has only 8 values.

# Date columns
contracts['contract_date'] = pd.to_datetime(contracts['contract_date'])
contracts['start_date'] = pd.to_datetime(contracts['start_date'])
contracts['end_date'] = pd.to_datetime(contracts['end_date'])

# Checking updates
print(contracts.info())

# We have also categorical column like industry, category, region, and city. In case of necessity, those columns will be defined as categories later.

# Unique values of each column
print(contracts.nunique())
# 8123 unqiue shop id.
# There are rows with the same package order id!
print(contracts[contracts.duplicated(subset='package_order_id', keep=False)].sort_values('package_order_id'))
# According to industry and category columns, these two orders are different from each other; however, their shop id, package_name, start_date and end_date and even their city and region is identical!
# There must be a mistake at data entry stage. Due to high uncertainty, all four rows are discarded from the following analysis.
contracts.drop_duplicates(subset='package_order_id', keep=False, inplace=True)

# Missing values
missing_conditions = contracts['contract_date'].isna() | contracts['start_date'].isna() | contracts['region'].isna()
print(contracts[missing_conditions])
# NaT for date columns and NaN for other types are both standard ways of missingness indications.

# Month column 
contracts['month'] = contracts['end_date'].dt.month
# If real_end_date exists
contracts['month'] = np.where(contracts['real_end_date'].notnull(), contracts['real_end_date'].dt.month, contracts['end_date'].dt.month)

# Months available in this data set
print(contracts['month'].unique())

# Let's do the calculation for the last three months of year (i.e. October, November, and December)



# TASK 1
contracts_sorted = contracts.sort_values(by = ['shop_id', 'start_date'])
contracts_sorted['start_date_next'] = contracts_sorted.groupby('shop_id')['start_date'].shift(-1)

contracts_sorted['days_to_new'] = contracts_sorted['start_date_next'] - contracts_sorted['end_date'] 
# If real_end_date exists:
contracts_sorted['days_to_new'] = np.where(contracts_sorted['real_end_date'].notnull(), contracts_sorted['start_date_next'] - contracts_sorted['real_end_date'], contracts_sorted['days_to_new'])

# Days to the next contract
contracts_sorted['days_to_new'] = contracts_sorted['days_to_new'].dt.days
# Renew
contracts_sorted['renew'] = contracts_sorted['days_to_new'] <= 30
# Return
contracts_sorted['return'] = contracts_sorted['days_to_new'] > 30

# Number of Renews Contracts
print(contracts_sorted['renew'].value_counts())

# Number of Returned Contracts
print(contracts_sorted['return'].value_counts())

# Renew and return rates
# Filter for October, November, and December
condition_months = contracts_sorted['month'].isin([10, 11, 12])
contracts_endseason = contracts_sorted[condition_months]

# Group by category, region, and month
renew_return_rates = contracts_endseason.groupby(['region', 'category', 'month'])['renew', 'return'].agg(lambda x: np.mean(x) * 100)
renew_return_rates = renew_return_rates.reset_index()

# Revise column name for clarity
renew_return_rates.rename(columns = {'renew':'renew_rate_perc', 'return':'return_rate_perc'}, inplace = True)

# print renew and return dataframe
renew_return_rates

# Data Visualization for renew rates in percent
sns.histplot(x = 'renew_rate_perc', data = renew_return_rates)
plt.xlabel('Renew Rate %')
plt.show()

sns.histplot(x = 'return_rate_perc', data = renew_return_rates, binwidth=10)
plt.xlabel('Renew Rate %')
plt.show()