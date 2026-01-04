import json
import pandas as pd

with open("leaderboard/artifacts/leaderboard.json") as f:
    data = json.load(f)

df = pd.DataFrame(data["models"])
df.to_csv("leaderboard/artifacts/leaderboard.csv", index=False)

print("CSV exported")
