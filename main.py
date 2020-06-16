import time
from enum import Enum, auto
import random


class States(Enum):
    IDLE = auto()
    FACE_RECOGNITION = auto()
    TEMPERATURE_CHECK_STATE = auto()
    MARK_ATTENDANCE_STATE = auto()
    DISPENSE_LIQUID_STATE = auto()
    ERROR_STATE = auto()


class MachineObject:

    def __init__(self):
        self.__state = States.IDLE

    def set_state(self, state):
        self.__state = state

    def get_state(self):
        return self.__state


class Machine(MachineObject):
    def __init__(self):
        super().__init__()


# Instantiate MachineObject class
machine = Machine()

# Some Flags used in program
MotionDetected = True                               # changes value to true if Motion is detected.
employee_matched = True                             # should be true if employee is matched with exisiting record
thermal_screening_passed = True                     # Should be true if thermal screening is passed.

"""
Functions to be written
"""
# Check temperature
def checkTemperature():
    """
        It should return the temperature in Degree Farenheit
        :return: Boolean
    """
    temperature = random(95,101)
    return temperature

# Recognise Face
def recognize_face():
    pass

# Detect Motion / Proximity
def detectMotion():
    """
    It should return True or False based on motion.
    :return: Boolean
    """
    pass

def MarkAttendance(emp_id):
    """

    :param emp_id: Takes in the employee ID returned by the face recognizer.
    :return: Name of the employee .
    """


def print_header():

    print("Welcome to Smart Sanitizer Dispenser.")
    print("Please come in front of the device. ")
    print()



"""
This is the main loop where execution takes place.
"""
def main():

    print_header()

#   Write the state Machine Logic Here.


if __name__ == '__main__':
    main()