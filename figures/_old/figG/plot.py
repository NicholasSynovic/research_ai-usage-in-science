import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame, Series

df: DataFrame = pandas.read_csv("uses_dl.csv")
df = df[
    [
        "Gemma3 Accuracy",
        "Phi Accuracy",
        "DeepSeek-R1 Accuracy",
        "Granite Accuracy",
        "GPT-OSS Accuracy",
        "Magistral Accuracy",
    ]
]
df.columns = df.columns.str.replace(pat=" Accuracy", repl="")

data: Series = df.iloc[-1]
data = data.sort_values(ascending=False)

sns.barplot(data=data)
plt.title(label="LLM Performance On Deep Learning Usage Identification")
plt.xlabel(xlabel="Large Language Model (LLM)")
plt.ylabel(ylabel="Accuracy To Human Performance")
plt.savefig("figG.pdf")
