
import numpy as np
import pandas as pd

# Load the array from the .npy file
lines_array = np.load('data.npy')

positive_lines_array = []
negative_lines_array = []

def polar_to_slope_intercept(polar_array):
    # Convert polar coordinates to slope-intercept form (m, c)
    m_values = np.tan(polar_array[:, 1])
    c_values = polar_array[:, 0] / np.cos(polar_array[:, 1])

    return m_values, c_values

# Convert to slope-intercept form
m_values, c_values = polar_to_slope_intercept(lines_array)

# Create a DataFrame to hold the results
# Stricktly speaking, this is not necessary, and a waste of memory, but it makes the code easier to read
result_df = pd.DataFrame({'r': lines_array[:,0], 'theta': lines_array[:,1], 'm': m_values, 'c': c_values, 'score': lines_array[:,2]})

# Split into positive and negative gradient lines
positive_lines_df = result_df[result_df['m'] > 0]
negative_lines_df = result_df[result_df['m'] <= 0]

# Find the x-intercept of each line (when y = 0, x-intercept = -c/m)
def x_intercept(m, c):
    return -c / m
    
# Create a new array that contains the x-intercept difference for each pair of lines
x_intercept_diff = []
for pos_line in positive_lines_df.itertuples():
    for neg_line in negative_lines_df.itertuples():
        try:
            x_intercept_pos = x_intercept(pos_line.m, pos_line.c)
            x_intercept_neg = x_intercept(neg_line.m, neg_line.c)
        except ZeroDivisionError:
            # Ignore lines with zero gradient / infinite intercept
            continue
        x_intercept_diff.append([pos_line.m, pos_line.c, neg_line.m, neg_line.c, np.abs(x_intercept_pos - x_intercept_neg), pos_line.score + neg_line.score])

# Sort the array based on the x-intercept difference and keep only the top 100 closest pairs
x_intercept_diff = np.array(x_intercept_diff)
sorted_indices = np.argsort(x_intercept_diff[:, 4])
top_100_pairs = x_intercept_diff[sorted_indices[:100]]

# Create a pandas DataFrame from the top 100 pairs
columns = ['Positive_Gradient_m', 'Positive_Intercept_c', 'Negative_Gradient_m', 'Negative_Intercept_c', 'X_Intercept_Difference', 'Score_Sum']
df = pd.DataFrame(top_100_pairs, columns=columns)

# Save the DataFrame to a .csv file
df.to_csv('closest_pairs.csv', index=False)