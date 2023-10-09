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

# contract_date, start_date, and end_date should be transformed into datatime objects.
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

# Pivoted renew return table
pivoted_renew_return = pd.melt(renew_return_rates, id_vars=['region', 'category', 'month'], var_name = 'renew_return', value_name='percent')

# Box plot
sns.boxplot(x = 'renew_return', y = 'percent', data = pivoted_renew_return)
plt.xlabel('Renew vs. Return')
plt.ylabel('Percent')
plt.show()

# Clearly, the longer it takes since the last contract, the higher the probability of customer churn. 

# Low rates of renewal
# It's not implied what percentage rates should alarm us, so a wise thing to do is to use quartiles of its distribution.
renew_quartiles = np.quantile(renew_return_rates['renew_rate_perc'], q = [0.25, 0.5, 0.75])

print(f'The first quartile of renew distribution is: {renew_quartiles[0]:.2f}')
print(f'The second quartile (median) of renew distribution is: {renew_quartiles[1]:.2f}')
print(f'The third quartile of renew distribution is: {renew_quartiles[2]:.2f}')

print(renew_return_rates[renew_return_rates['renew_rate_perc'] == 0])

# Renew across region
sns.boxplot(x = 'renew_rate_perc', y = 'region', data = renew_return_rates)
plt.xlabel('Percent')
plt.ylabel('Region')
plt.show()

print(
'''
Regions with lowest renewal rates are:
Booshehr, Khorasan Jonubi, Charmahal Bakhtiari, Yazd, Kerman, Kermanshah, and Khorasan Shomali
'''
)

# Renew across category
sns.boxplot(x = 'renew_rate_perc', y = 'category', data = renew_return_rates)
plt.xlabel('Percent')
plt.ylabel('Category')
plt.show()

print(
'''
Categories with lowest renewal rates are:
Khodro, Lavazem shakhsi, and Mobile-tablet.
'''
)

# package_name, listing_limit, and industry table
contracts_dummies = pd.concat([contracts[['region', 'category', 'month','Listing_limit']], pd.get_dummies(contracts['package_name']), pd.get_dummies(contracts['industry'])], axis=1)

contracts_dummies = contracts_dummies.groupby(['region', 'category', 'month']).mean().reset_index()
contracts_dummies = contracts_dummies[contracts_dummies['month'].isin([10, 11, 12])]

merged_df = renew_return_rates.merge(contracts_dummies, how='inner', on = ['region', 'category', 'month'])
pd.melt(merged_df, id_vars=['general', 're_auto'])

# Car Industry
sns.scatterplot(x = 'Car A', y = 'renew_rate_perc', data = merged_df[merged_df['Car A'] != 0])
plt.show()

sns.scatterplot(x = 'Car B', y = 'renew_rate_perc', data = merged_df[merged_df['Car B'] != 0])
plt.show()

sns.scatterplot(x = 'Car C', y = 'renew_rate_perc', data = merged_df[merged_df['Car C'] != 0])
plt.show()

# General Industry
sns.scatterplot(x = 'General A', y = 'renew_rate_perc', data = merged_df[merged_df['General A'] != 0])
plt.show()

sns.scatterplot(x = 'General B', y = 'renew_rate_perc', data = merged_df[merged_df['General B'] != 0])
plt.show()

sns.scatterplot(x = 'General C', y = 'renew_rate_perc', data = merged_df[merged_df['General C'] != 0])
plt.show()

# Real Estate
sns.scatterplot(x = 'Real Estate A', y = 'renew_rate_perc', data = merged_df[merged_df['Real Estate A'] != 0])
plt.show()

sns.scatterplot(x = 'Real Estate B', y = 'renew_rate_perc', data = merged_df[merged_df['Real Estate B'] != 0])
plt.show()

sns.scatterplot(x = 'Real Estate C', y = 'renew_rate_perc', data = merged_df[merged_df['Real Estate C'] != 0])
plt.show()

# Box Plots
sns.boxplot(x = 'general', y = 'renew_rate_perc', data = merged_df)
plt.show()

sns.boxplot(x = 're_auto', y = 'renew_rate_perc', data = merged_df)
plt.show()

# Renewal rate vs. Listing
sns.scatterplot(x = 'Listing_limit', y = 'renew_rate_perc', data = merged_df)
plt.show()