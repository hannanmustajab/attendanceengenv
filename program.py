from threading import Thread
import time
import random

# Set to false to disable testing/tracing code
from face_recognizer import startCapture
from infrastructure.temperature import checkTemperature

VERBOSE_MODE = True

# States
IDLE_STATE = 0
FACE_RECOGNITION = 1
TEMPERATURE_CHECK_STATE = 2
MARK_ATTENDANCE_STATE = 3
DISPENSE_LIQUID_STATE = 4
ERROR_STATE = 5

################################################################################
# Setup hardware


# Set the time for testing
# Once finished testing, the time can be set using the REPL using similar code
if VERBOSE_MODE:
    print("VERBOSE MODE ON")

################################################################################
# Variables
MotionDetected = 1  # changes value to true if Motion is detected.
# timer = threading.Timer(15.0)
temperature_threshold = 99.8


################################################################################
# Support functions

def log(s):
    """Print the argument if testing/tracing is enabled."""
    if VERBOSE_MODE:
        print(s)


# Check temperature Function
checkTemperature()


# Detect Motion / Proximity
def detectMotion():
    """
    It should return True or False based on motion.
    :return: Boolean
    """
    global MotionDetected
    MotionDetected = False
    return MotionDetected

state = IDLE_STATE

################################################################################
# Infinite Loop Starts Here.
while True:
    test_trigger = False

    # IDLE state

    if state == IDLE_STATE:
        log("IDLE")
        time.sleep(2)
        if VERBOSE_MODE:
            print("IDLE")
        print(detectMotion)
        if MotionDetected:
            state = FACE_RECOGNITION
            print("Motion Detected")
        continue

    # FACE_RECOGNITION State
    if state == FACE_RECOGNITION:
        if VERBOSE_MODE:
            print("FACE_RECOGNITION")

        # Start capturing video feed.
        Thread(target=startCapture())

        # If employee is found, Then move to temperature checking state.
        if startCapture() is True:
            print("Captured...")
            state = TEMPERATURE_CHECK_STATE
            continue
        else:
            state = IDLE_STATE

        time.sleep(1)

        continue

    # TEMPERATURE_CHECK_STATE State
    if state == TEMPERATURE_CHECK_STATE:
        if VERBOSE_MODE:
            print("TEMPERATURE_CHECK_STATE")
        time.sleep(1)

        # Check temperature
        current_temperature = checkTemperature()
        if current_temperature < temperature_threshold:
            state = MARK_ATTENDANCE_STATE
            continue
        elif current_temperature > temperature_threshold:
            print(temperature_threshold)
            print("Access Denied!")
            state = IDLE_STATE

    # MARK_ATTENDANCE_STATE State
    if state == MARK_ATTENDANCE_STATE:
        if VERBOSE_MODE:
            print("MARK ATTENDANCE")
        time.sleep(1)
        state = DISPENSE_LIQUID_STATE
        continue

    # DISPENSE_LIQUID_STATE State
    if state == DISPENSE_LIQUID_STATE:
        if VERBOSE_MODE:
            print("DISPENSING")
        time.sleep(1)
        state = IDLE_STATE
        continue
