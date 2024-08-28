import pandas as pd

# Read the CSV file
df = pd.read_csv('5lines.csv')

# Reduce to only the first 5 rows
df_reduced = df.head(5)

# Save back to the same CSV file
df_reduced.to_csv('5lines.csv', index=False)

print("The file has been reduced to 5 rows and saved.")