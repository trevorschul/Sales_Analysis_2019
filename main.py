import pandas as pd
import os
import matplotlib.pyplot as plt
from itertools import combinations
from collections import Counter

# concat monthly files into yearly file

year_data = pd.DataFrame()
files = [file for file in os.listdir('./sale_data')]

for file in files:
    df = pd.read_csv(f'./sale_data/{file}')
    year_data = pd.concat([year_data, df])

year_data.to_csv('year_data.csv', index=False)
year_data = pd.read_csv('year_data.csv')

# Drop null rows

nan_df = year_data[year_data.isna().any(axis=1)]
year_data = year_data.dropna(how="all")

# Delete rows with text in order date columns

year_data = year_data[year_data['Order Date'].str[0:2] != 'Or']

# Convert number string columns to correct data type

year_data['Quantity Ordered'] = pd.to_numeric(year_data['Quantity Ordered'])
year_data['Price Each'] = pd.to_numeric(year_data['Price Each'])

# insert month column

year_data['Month'] = year_data['Order Date'].str[0:2]
year_data['Month'] = year_data['Month'].astype('int32')

# insert city column

# def get_city(address):
#     return address.split(",")[1]

year_data["City"] = year_data["Purchase Address"].apply(lambda x: x.split(",")[1] + " " + x.split(",")[2].split(" ")[1])

# create per order sales column

year_data["Sales"] = year_data["Quantity Ordered"] * year_data["Price Each"]

# What was best sales month?

sales_by_month = year_data.groupby("Month").sum()

plt.bar(range(1,13), sales_by_month["Sales"])
plt.xticks(range(1,13))
plt.ylabel("Sales")
plt.xlabel("Month Number")
plt.show()

# What was the city with highest sales

sales_by_city = year_data.groupby("City").sum()

cities = [city for city, df in year_data.groupby("City")]

plt.bar(cities, sales_by_city["Sales"])
plt.xticks(cities, rotation ="vertical", size=8)
plt.ylabel("Sales")
plt.xlabel("City")
plt.show()

# Show peak order times to know best time to display ads

year_data["Order Date"] = pd.to_datetime(year_data["Order Date"])
year_data["Hour"] = year_data["Order Date"].dt.hour

hours = [hour for hour, df in year_data.groupby("Hour")]

plt.plot(hours, year_data.groupby("Hour").count())
plt.xticks(hours)
plt.grid()
plt.ylabel("Sales")
plt.xlabel("Hour")
plt.show()

# What products are sold together

# Find duplicated order IDs
df = year_data[year_data["Order ID"].duplicated(keep=False)]

df["Grouped"] = df.groupby("Order ID")["Product"].transform(lambda x: ",".join(x))

df = df[["Order ID", "Grouped"]].drop_duplicates()

# Create dictionary of items commonly ordered together

count = Counter()


# Can change 2 to any number to determine if multiple items are ordered together
for row in df["Grouped"]:
    row_list = row.split(",")
    count.update(Counter(combinations(row_list, 2)))

for key,value in count.most_common(10):
    print(key, value)

# What product sold the most and why?

product_group = year_data.groupby("Product")
quantity_ordered = product_group.sum()["Quantity Ordered"]

products = [product for product, df in product_group]
plt.bar(products, quantity_ordered)
plt.xticks(products, rotation="vertical", size=6)
plt.ylabel("Quantity Ordered")
plt.xlabel("Product")
plt.show()

prices = year_data.groupby("Product").mean()["Price Each"]

# Overlay prices and quantity to see if that affects order size

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.bar(products, quantity_ordered)
ax2.plot(products, prices, "b-")

ax1.set_xlabel("Product Name")
ax1.set_ylabel("Quantity Ordered")
ax2.set_xlabel("Price")
ax1.set_xticklabels(products, rotation="vertical", size=6)
plt.show()
