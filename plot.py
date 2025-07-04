import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

h2_df = pd.read_json('h2_perf_timings.json')
h2_df["type"] = "h2"
h3_df = pd.read_json('h3_perf_timings.json')
h3_df["type"] = "h3"

df = pd.concat([h2_df, h3_df])

df["loadingTime"] = df["responseEnd"] - df["requestStart"]

fig, ax = plt.subplots(1, 1, figsize=(12, 6))

sns.boxplot(y='loadingTime', hue="type", data=df)

plt.savefig('plot.svg')