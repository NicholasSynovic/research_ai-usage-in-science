# import pandas
# from pandas import DataFrame
# import matplotlib.pyplot as plt
# import numpy as np
# import seaborn
# import click
# from pathlib import Path

# seaborn.set_theme(style='white')
# df = pandas.read_csv('pivotTable.csv', skiprows=1)

# #clean up csv file from pivot table
# df.columns = ["Year", "Adaptation", "Conceptual", "Deployment", "Total"]

# #filter/drop grand total row and total column
# df = df[df["Year"] != "Grand Total"]  #
# df = df.drop(columns=["Total"])
# df['Year'] = pandas.to_numeric(df['Year'])


# plt.xlabel("Year")
# plt.ylabel("Count")
# plt.title("Trends of DL Reuse Processes (2017 - 2024)")
# plt.legend(title="Reuse Type")
# plt.ylim(0, 10)
# plt.show()


import matplotlib.pyplot as plt
import pandas
import seaborn

seaborn.set_theme(style="white")
df = pandas.read_csv("pivotTable.csv", skiprows=1)

# Clean up CSV file from pivot table
df.columns = ["Year", "Adaptation", "Conceptual", "Deployment", "Total"]
df = df[df["Year"] != "Grand Total"]
df = df.drop(columns=["Total"])
df["Year"] = pandas.to_numeric(df["Year"])

# Plot and skip year column
plt.figure(figsize=(10, 6))

# Set to store already annotated points
annotated_points = set()

for column in df.columns[1:]:
    x = df["Year"]
    y = df[column]
    plt.plot(x, y, marker="o", label=column)

    for i, value in enumerate(y):
        # Check if this point has already been annotated
        coord = (x[i], y[i])
        if coord not in annotated_points:
            plt.text(
                x[i] + 0.02,
                y[i] + 0.13,
                f"{value}",
                ha="right",
                va="bottom",
                fontsize=8,
            )
            annotated_points.add(coord)  # Add the coordinate to the set

plt.xlabel("Year")
plt.ylabel("Count")
plt.title("Trends of DL Reuse Processes (2017 - 2024)")
plt.legend(title="Reuse Type")
plt.ylim(0, 10)
plt.show()
