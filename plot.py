import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame()

for folder in ["skydsl", "konnect", "starlink"]:
    h2_df = pd.read_json(f'{folder}/h2_perf_timings.json')
    h2_df["provider"] = f"{folder}"
    h2_df["type"] = "HTTP/2 (with PEP)"
    h2_df["loadingTime"] = h2_df["domComplete"] - h2_df["connectStart"]
    h3_df = pd.read_json(f'{folder}/h3_perf_timings.json')
    h3_df["provider"] = f"{folder}"
    h3_df["type"] = "Careful Resume"
    h3_df["loadingTime"] = h3_df["domComplete"] - h3_df["connectStart"]

    df = pd.concat([df, h2_df, h3_df])

fig, ax = plt.subplots(1, 1, figsize=(12, 6))

sns.boxplot(y='loadingTime', x="provider", hue="type", data=df, ax=ax)

plt.show()
plt.savefig('plot.svg')