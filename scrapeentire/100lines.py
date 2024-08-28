import pandas as pd

# Read the CSV file
df = pd.read_csv('export_members41113-1-1724283589final.csv')

# Reduce to only the first 5 rows
df_reduced = df.head(100)

# Save back to the same CSV file
df_reduced.to_csv('100lines.csv', index=False)

print("The file has been reduced to 5 rows and saved.")