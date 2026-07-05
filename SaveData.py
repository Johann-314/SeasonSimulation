import pandas as pd
import numpy as np
import os
from datetime import datetime

def flatten_matches(matches, tournament_name):
    rows = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for (teamA, teamB), sets in matches:
        flat = {
            "tournament": tournament_name,
            "timestamp": timestamp,
            "teamA": teamA,
            "teamB": teamB
        }
        for i, (a, b) in enumerate(sets, start=1):
            flat[f"set{i}A"] = a
            flat[f"set{i}B"] = b
        rows.append(flat)

    return pd.DataFrame(rows)

def load_history(path):
    if os.path.exists(path):
        if path.endswith(".csv"):
            return pd.read_csv(path)
        else:
            return pd.read_excel(path)
    return pd.DataFrame()

def save_history(df, path):
    if path.endswith(".csv"):
        df.to_csv(path, index=False)
    else:
        df.to_excel(path, index=False)

def update_history(matches, tournament_name, path="Random\SeasonSimulation\data.xlsx"):
    new_df = flatten_matches(matches, tournament_name)
    old_df = load_history(path)

    # Append new block; do NOT drop duplicates (historical log!)
    combined = pd.concat([old_df, new_df], ignore_index=True)

    save_history(combined, path)
    return combined

def load_tournament(tournament_name,path="Random\SeasonSimulation\data.xlsx"):
    # Load historical file
    if not os.path.exists(path):
        raise FileNotFoundError(f"No historical file found at {path}")

    if path.endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    # Filter by tournament name
    df_tournament = df[df["tournament"] == tournament_name]

    # Convert back to your original nested list structure
    result = []
    for _, row in df_tournament.iterrows():
        teamA = row["teamA"]
        teamB = row["teamB"]

        # Extract all set columns dynamically
        sets = []
        i = 1
        while f"set{i}A" in row and f"set{i}B" in row:
            if (not np.isnan([row[f"set{i}A"]])) and (not np.isnan(row[f"set{i}B"])):
                sets.append([int(row[f"set{i}A"]), int(row[f"set{i}B"])])
            i += 1

        result.append([[teamA, teamB], sets])

    return result
