import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Data
data = {
    "Category": ["Deep Learning", "Model Weights", "Deep Neural Network"],
    "Total": [54, 50, 5],
}

# Create a DataFrame from the data
df = pd.DataFrame(data)
df = df.sort_values(by="Total", ascending=False)

# Create a bar plot using seaborn
sns.barplot(x="Category", y="Total", data=df)

# Add labels and title to the plot
plt.xlabel("Keyword")
plt.ylabel("Number Of Papers")
plt.title("Number Of Papers Randomly Sampled By Keyword")

for i, v in enumerate(df["Total"]):
    plt.text(i, v + 0.1, str(v), color="black", ha="center")

plt.tight_layout()
plt.savefig("sampleKeywords.png")
