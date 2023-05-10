import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

hands = [
    'AAo', 'AQs', 'KJs', 'A5s', 'K9o', 'K6s', 'K4s', 'J9o', 'K3o', 'J5s',
    '87s', '86s', '96o', '95o', '94o', '43s', '73o', '32o'
]

# hands = [
#     'AAo', 'AQs'
# ]

# read preflop_equity.csv
df = pd.read_csv('preflop_equity.csv', header=None)

# x axis will be the number of players  1 to 10
x = np.arange(1, 11)

# select the row with the hands from the hands array
# and convert it to a numpy array
y = np.array(df.loc[df[0].isin(hands)].iloc[:, 1:])

# remove the % sign from the end of each value and convert to float
y = np.array([list(map(lambda x: float(x[:-1]), row)) for row in y])

# axes titles 
plt.xlabel('Number of Players')
plt.ylabel('Win Percentage')

# plot title 
plt.title('Preflop Win Percentage vs. Number of Players')

# change y-axis labels intervals
plt.yticks(np.arange(0, 101, 5))

# plot line graphs for each hand
for i in range(len(hands)):
    plt.plot(x, y[i], label=hands[i])

# make a legend
plt.legend()

plt.show()
