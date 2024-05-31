from __future__ import print_function

import time
from sr.robot import *

# Constants for orientation and distance control
ORIENTATION_THRESHOLD = 2.0
DISTANCE_THRESHOLD = 0.4

# Initialize the robot instance
robot = Robot()

# List to keep track of grabbed gold box codes
grabbed_gold_codes = []

def drive(speed, duration):
    """
    Sets the robot's linear velocity.
    
    Args:
    speed (int): The speed of the wheels.
    duration (int): The duration to drive in seconds.
    """
    robot.motors[0].m0.power = speed
    robot.motors[0].m1.power = speed
    time.sleep(duration)
    robot.motors[0].m0.power = 0
    robot.motors[0].m1.power = 0

def turn(speed, duration):
    """
    Sets the robot's angular velocity.
    
    Args:
    speed (int): The speed of the wheels.
    duration (int): The duration to turn in seconds.
    """
    robot.motors[0].m0.power = speed
    robot.motors[0].m1.power = -speed
    time.sleep(duration)
    robot.motors[0].m0.power = 0
    robot.motors[0].m1.power = 0

def find_gold_token():
    """
    Finds the closest golden token that hasn't been grabbed yet.
    
    Returns:
    (float, float, int): Distance, angle, and code of the closest golden token. Returns -1, -1, -1 if no token is found.
    """
    closest_distance = 100
    closest_token = None

    for token in robot.see():
        if token.dist < closest_distance and token.info.marker_type == MARKER_TOKEN_GOLD and token.info.code not in grabbed_gold_codes:
            closest_distance = token.dist
            closest_token = token

    if closest_token is None:
        return -1, -1, -1
    else:
        return closest_token.dist, closest_token.rot_y, closest_token.info.code

def find_release_location():
    """
    Finds the closest drop location among the grabbed golden tokens.
    
    Returns:
    (float, float, int): Distance, angle, and code of the closest drop location. Returns -1, -1, -1 if no location is found.
    """
    closest_distance = 100
    closest_location = None

    for token in robot.see():
        if token.dist < closest_distance and token.info.marker_type == MARKER_TOKEN_GOLD and token.info.code in grabbed_gold_codes:
            closest_distance = token.dist
            closest_location = token

    if closest_location is None:
        return -1, -1, -1
    else:
        return closest_location.dist, closest_location.rot_y, closest_location.info.code

def grab_gold():
    """
    Moves towards the closest ungrabbed gold token and grabs it.
    """
    while True:
        dist, rot_y, code = find_gold_token()
        if dist == -1:
            print("No gold token found, searching...")
            turn(5, 2)
        elif dist <= DISTANCE_THRESHOLD:
            print("Found a gold token!")
            break
        elif -ORIENTATION_THRESHOLD <= rot_y <= ORIENTATION_THRESHOLD:
            print("Moving forward...")
            drive(10, 0.5)
        elif rot_y < -ORIENTATION_THRESHOLD:
            print("Turning left...")
            turn(-2, 0.5)
        elif rot_y > ORIENTATION_THRESHOLD:
            print("Turning right...")
            turn(2, 0.5)

def release_gold():
    """
    Moves towards the closest drop location and releases the gold token.
    """
    while True:
        dist, rot_y, code = find_release_location()
        if dist == -1:
            print("No drop location found, searching...")
            turn(5, 2)
        elif dist < DISTANCE_THRESHOLD + 0.2:
            print("Found a drop location!")
            break
        elif -ORIENTATION_THRESHOLD <= rot_y <= ORIENTATION_THRESHOLD:
            print("Moving forward...")
            drive(10, 0.5)
        elif rot_y < -ORIENTATION_THRESHOLD:
            print("Turning left...")
            turn(-2, 0.5)
        elif rot_y > ORIENTATION_THRESHOLD:
            print("Turning right...")
            turn(2, 0.5)

def main():
    """
    Main function to search, grab, and relocate gold tokens.
    """
    while len(grabbed_gold_codes) < 6:
        dist, rot_y, code = find_gold_token()
        while dist == -1:
            print("Searching for a gold token...")
            turn(5, 2)
            dist, rot_y, code = find_gold_token()
        
        grab_gold()
        robot.grab()
        print("Gold token grabbed!")

        if len(grabbed_gold_codes) == 0:
            # First drop location: move to a predefined location
            turn(-10, 1.1)
            drive(10, 19)
        else:
            # Find the nearest previous drop location
            dist, rot_y, code = find_release_location()
            while dist == -1:
                print("Searching for a drop location...")
                turn(5, 2)
                dist, rot_y, code = find_release_location()
            release_gold()

        robot.release()
        print("Gold token released!")
        drive(-10, 2)
        turn(30, 2)
        grabbed_gold_codes.append(code)


main()

