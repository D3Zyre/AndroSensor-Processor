import csv
import matplotlib.pyplot as plt
from datetime import datetime
from math import sqrt, cos, sin, acos
from numpy import linalg, dot

print("defining variables...")

filename = "Sensor_record_20230804_171014_AndroSensor.csv"

unit_gravity = (0, 0, 1)

X_accelerations: list[float] = []
Y_accelerations: list[float] = []
Z_accelerations: list[float] = []

X_car_accelerations: list[float] = []
Y_car_accelerations: list[float] = []
Z_car_accelerations: list[float] = []

X_gravities: list[float] = []
Y_gravities: list[float] = []
Z_gravities: list[float] = []

sum_accelerations: list[float] = []
seconds_since_starts: list[float] = []


def find_index(string: str, list_to_look_in: list[str]) -> int:
    """
    finds the index in the list which contains string
    """
    index = 0
    for item in list_to_look_in:
        if item.find(string) != -1:
            break
        index += 1

    return index

print("loading file into memory...")

with open(filename, 'r', encoding = "UTF-8") as file:
    reader = csv.reader(file)
    rows = [row for row in reader] # read the whole file

print("finding indices...")

# find column indices of variables
X_acceleration_index = find_index("LINEAR ACCELERATION X (m/s²)", rows[0])
Y_acceleration_index = find_index("LINEAR ACCELERATION Y (m/s²)", rows[0])
Z_acceleration_index = find_index("LINEAR ACCELERATION Z (m/s²)", rows[0])

X_gravity_index = find_index("GRAVITY X (m/s²)", rows[0])
Y_gravity_index = find_index("GRAVITY Y (m/s²)", rows[0])
Z_gravity_index = find_index("GRAVITY Z (m/s²)", rows[0])

milliseconds_index = find_index("Time since start in ms ", rows[0])

print("processing data...")

for row in rows[1:]:
    seconds_since_start = float(row[milliseconds_index])/1000

    X_acceleration = float(row[X_acceleration_index])
    Y_acceleration = float(row[Y_acceleration_index])
    Z_acceleration = float(row[Z_acceleration_index])

    X_gravity = float(row[X_gravity_index])
    Y_gravity = float(row[Y_gravity_index])
    Z_gravity = float(row[Z_gravity_index])

    # append data to lists
    seconds_since_starts.append(seconds_since_start)

    X_accelerations.append(X_acceleration)
    Y_accelerations.append(Y_acceleration)
    Z_accelerations.append(Z_acceleration)

    X_gravities.append(X_gravity)
    Y_gravities.append(Y_gravity)
    Z_gravities.append(Z_gravity)

    sum_accelerations.append(sqrt(X_acceleration**2 + Y_acceleration**2 + Z_acceleration**2))

average_gravity = (sum(X_gravities)/len(X_gravities), sum(Y_gravities)/len(Y_gravities), sum(Z_gravities)/len(Z_gravities))
gravity_magnitude = sqrt(sum([i**2 for i in average_gravity]))
unit_average_gravity = tuple([i/gravity_magnitude for i in average_gravity]) # direction of negative Z
# this is where world -Z is in terms of phone XYZ

# now rotate XYZ accelerations to put -Z in the direction of gravity
# https://en.wikipedia.org/wiki/Rotation_matrix
# using Talt-Bryan angles
gamma = 0 # rotation about Z-axis
beta = 0 # rotation about Y-axis
alpha = -acos(dot(unit_average_gravity, unit_gravity)) # rotation about X-axis
convert_phone_XYZ_into_car_XYZ_matrix = ((cos(beta)*cos(gamma), sin(alpha)*sin(beta)*cos(gamma) - cos(alpha)*sin(gamma), cos(alpha)*sin(beta)*cos(gamma) + sin(alpha)*sin(gamma)),
                                         (cos(beta)*sin(gamma), sin(alpha)*sin(beta)*sin(gamma) + cos(alpha)*cos(gamma), cos(alpha)*sin(beta)*sin(gamma) - sin(alpha)*cos(gamma)),
                                         (-sin(beta), sin(alpha)*cos(beta), cos(alpha)*cos(beta)))

for i in range(len(X_gravities)):
    X_car_acceleration, Y_car_acceleration, Z_car_acceleration = tuple(linalg.solve(convert_phone_XYZ_into_car_XYZ_matrix, (X_gravities[i], Y_gravities[i], Z_gravities[i])))
    X_car_accelerations.append(X_car_acceleration)
    Y_car_accelerations.append(Y_car_acceleration)
    Z_car_accelerations.append(Z_car_acceleration)

print("plotting...")

# Plot 0: sum of XYZ acceleration
plt.figure(0)
plt.scatter(seconds_since_starts, sum_accelerations, s = 3)

plt.xlabel("Time from Start (s)")
plt.ylabel("Net Acceleration (m/s²)")
plt.title("Net Acceleration of Beedle, Driving from Windsor Parkade to Home")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()

# Plot 1: X, Y and Z acceleration on the same plot
plt.figure(1)
plt.scatter(seconds_since_starts, X_car_accelerations, s=3)
plt.scatter(seconds_since_starts, Y_car_accelerations, s=3)
plt.scatter(seconds_since_starts, Z_car_accelerations, s=3)

plt.xlabel("Time from Start (s)")
plt.ylabel("Linear Acceleration (m/s²)")
plt.title("Linear Acceleration of Beedle, Driving from Windsor Parkade to Home")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()

plt.legend(("X", "Y", "Z"))

print("done")

plt.show()