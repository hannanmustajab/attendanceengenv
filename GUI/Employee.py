#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 20:26:55 2019

@author: abdulhannanmustajab
"""
import os
import time
from datetime import timedelta, datetime

# Connection
from pymongo import MongoClient

# import Location

# import train_images as ft

cluster = MongoClient(
    "mongodb+srv://mustajabhannan:Hannan786@cluster0-n7aqf.mongodb.net/test?retryWrites=true&w=majority")

db = cluster["attendance"]
collection = db["users"]

location_collection = db["locations"]


class Employee:
    """Docstring of employee"""

    # Flag for trusted employee
    __flag = False  # Untrusted by default

    def __init__(self, emp_id):
        """Initialize class with First Name , Last Name and Employee ID"""
        self.emp_id = emp_id
        self.__flag = False

    def checkEmployee(self):
        """
        Check if employee exists with the ID.
        Returns true if employee exists.
        :rtype: object
        :return:
        """
        result = collection.find_one({"emp_id": self.emp_id})
        # result is none means employee does not exist.
        if result is None:
            return False
        return True

    def fullName(self):
        result = collection.find_one({"emp_id": int(self.emp_id)})
        if result is None:
            return ("No record found")
        else:
            firstName = result["first_name"]
            lastName = result["last_name"]
            return '{} {}'.format(firstName.capitalize(), lastName.capitalize())

    def addUser(self, first_name, last_name):
        """ Add user to the database,
        Employee is already initialized with an emp_id. Use this method to add it to the database.
        """
        if self.checkEmployee() is True:
            return "Employee Exists"

        if collection.find_one({"emp_id": self.emp_id}) is None:

            # Userdata to be added to database.
            userData = {

                "emp_id": self.emp_id,
                "first_name": first_name,
                "last_name": last_name

            }
            result = collection.insert_one(userData)

            # If data is successfully updated, Returns True else Returns False .
            if result.acknowledged:
                return True
            else:
                return False
        else:
            print("Employee Already Exists with ID: ", self.emp_id)

    def checkAttendance(self):
        """
        Check Attendance.
        Check if attendance is already marked for the day

        :return: Boolean ( True or False)
        :returns false if attendance is not marked.
        """
        if self.checkEmployee() is True:  # Check if employee exists with the ID.

            ts = time.time()
            date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            checkAttendance = collection.find({"$and": [{"emp_id": self.emp_id}, {"attendance.date": date}]})
            checkAttendance = list(checkAttendance)
            if checkAttendance == []:
                return False
            else:
                return True
        return "Employee Does Not Exist"

    def addAttendance(self, verified=False, method="manual"):
        """
        Add Attendance for the user each day.
        First it checks if the attendance is already marked or not.
        Takes the current timestamp and date and pushes it to the database.
        """
        if self.checkEmployee() is True:  # Check if employee exists with the ID.

            # TODO
            # "Mark attendance for trusted employees and alot special locations"

            # Make all checks before uploading data.
            penaltyCheck = self.checkPenalty()  # Returns true if penalised.
            attendanceCheck = self.checkAttendance()  # Returns True if attendance is already marked.
            dayOff = self.checkDayOff()

            if dayOff is True:
                return "Not Work Day!"
            else:

                ts = time.time()
                date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.fromtimestamp(ts).strftime('%H:%M:%S')

                # Case 1: If the user is marking attendance for the first time.

                firstAttendance = collection.find({"emp_id": self.emp_id},
                                                  {"attendance.date": date})
                location = self.__getLocation()

                if firstAttendance is None:
                    data = {
                        "attendance":
                            {
                                "date": date,
                                "time": timeStamp,
                                "location": location['locationID'],
                                "location_name": location['locationName'],
                                "verified": verified,
                                "method": method
                            }
                    }

                    collection.update(
                        {"emp_id": self.emp_id},
                        {"$push": data},
                        upsert=True
                    )

                    # Once attendance is added successfully, then update the location with available slots.

                    location_collection.update({"locationID": location['locationID']}
                                               , {"$inc": {"available_spots": -1}})
                    # Location.Location(int(location['locationID'])).resetSpots()

                    self.generateAttendancePDF()

                    return 'First Attendance Marked For {} at {}'.format(self.emp_id, location['locationName'])

                # Case 2 : If the user has no penalty and attendance isn't already marked.
                # elif penaltyCheck and attendanceCheck is False:
                elif attendanceCheck is False:

                    data = {
                        "attendance":
                            {
                                "date": date,
                                "time": timeStamp,
                                "location": location['locationID'],
                                "location_name": location['locationName'],
                                "verified": verified,
                                "method": method
                            }
                    }

                    collection.update(
                        {"emp_id": self.emp_id},
                        {"$push": data},
                        upsert=True

                    )

                    # Once attendance is added successfully, then update the location with available slots.

                    location_collection.update({"locationID": location['locationID']}
                                               , {"$inc": {"available_spots": -1}})
                    # Location.Location(int(location['locationID'])).resetSpots()

                    self.generateAttendancePDF()

                    return 'Attendance Marked For {} at {}'.format(self.fullName(), location['locationName'])

                elif attendanceCheck is True:
                    return "Attendance Already Marked"

                elif penaltyCheck is True:
                    return "Penalty Found"

                else:
                    return "Unknown Error"
        else:
            return "No Employee Found"

    def addPenalty(self, number_of_days):
        """
        Penalise the employee for being absent on a particular day.
        Takes input the number of days. It will penalise the employee for that particular number of days from the current date.
        His attendance wont be marked for those days then.
        """

        if self.checkEmployee() is True:  # Check if employee exists with the ID.

            base = datetime.today()
            date_list = [base + timedelta(days=x) for x in
                         range(number_of_days)]  # Returns a list of dates which are to be penalised.
            # date_array = []

            dateListLambda = list(map(lambda date: date.strftime("%x"),
                                      date_list))  # Doing the same thing as in the next line using Lambda Function.

            # for date in date_list:
            #     date = date.strftime("%x")
            #     date_array.append(date)

            data = {"penalty": dateListLambda}

            collection.update(
                {"emp_id": self.emp_id},
                {"$push": data},
                upsert=True

            )
            return ("Successfully Penalised For " + str(number_of_days) + " Days")
        return "No Record Found."

    def checkPenalty(self):
        """
        This function checks that if the employee is penalised for that particular day and returns true or false.
        """

        if self.checkEmployee() is True:  # Check if employee exists with the ID.

            ts = time.time()
            date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            dateforpenalty = datetime.fromtimestamp(ts).strftime('%m/%d/%y')
            checkPenalty = collection.find(
                {
                    "emp_id": self.emp_id
                },
                {
                    "penalty": dateforpenalty
                }
            )

            return list(checkPenalty)
            # if dateforpenalty in list(checkPenalty):
            #     return "Yes Date Found"
            # else:
            #     return "Date not found"

            # if checkPenalty is not None or not []:
            #     return checkPenalty
            #
            # else:
            #     return False
        else:
            return False

    def knowTrusted(self):
        # type: (self) -> bool
        """
        Get the data from database and check if the employee is trusted or not.
        """

        if self.checkEmployee() is False:  # Check if employee exists with the ID.
            return "No Record Found."

        if self.__flag is True:
            return True
        else:
            return False

    def setOffDay(self, day):
        """ Set weekly day off for each employee.
            Enter any integer between 0 and 6.
            Enter 0 for Monday and 6 for Sunday.
        """
        if self.checkEmployee() is False:  # Check if employee exists with the ID.
            return "No Record Found."

        if abs(int(day)) > 6:
            return "Error, Please enter valid input"
        else:
            offDay = day

        # Used upsert to create if not exists.
        collection.update(
            {
                "emp_id": self.emp_id
            },
            {
                "$set":
                    {
                        "offDay": offDay
                    }
            },
            upsert=True
        )

    def isWorkday(self):
        """
        Checks the database for the day off value and compares it with todays date. If it is a offday, then the employee isn't marked absent.
        Returns true if it is workday and false if it is not.
        """
        result = collection.find_one({"emp_id": self.emp_id})

        return result

    def viewAttendance(self):
        data = collection.find({"emp_id": self.emp_id}, {"attendance"})
        return data

    def __getLocation(self):
        # data = location_collection.find({"available_spots": {"$gt": 1}})
        try:
            data = location_collection.aggregate(
                [{"$match": {"available_spots": {"$gte": 1}}},

                 {"$sample": {"size": 1}}])
            data = list(data)
            data = data[0]
            self.locationData = data
            return data
        except Exception as e:
            print (e)

    def checkDayOff(self):
        """
        Check if it is a dayOff for the employee.
        :return: True if it is dayoff for the employee.
        """
        import datetime
        i = datetime.datetime.now()
        dayInteger = int(i.strftime('%w'))
        data = collection.find({"$and": [{"emp_id": self.emp_id}, {"offDay": dayInteger}]})
        data = list(data)
        if data == []:
            return False
        else:
            return True

    def viewDayOff(self):
        """
        Returns the name of the day.
        :return:
        """
        data = list(collection.find({"emp_id": self.emp_id}, {"offDay"}))
        try:
            return data[0]['offDay']
        except:
            return False

    def generateAttendancePDF(self):

        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        data = list(collection.find({"$and": [{"emp_id": self.emp_id}, {"attendance.date": date}]}))
        if len(data) is not 0:
            data = data[0]['attendance']

            for record in data:
                try:
                    if record['date'] == date:
                        locationName = record['location_name']
                        locationID = record['location']
                        timeStamp = record['time']
                        name = self.fullName()

                        os.chdir("includes")
                        txt_data = """
                            ###############
                            Proctor Office
                               DUTY SLIP
                            ###############
                            
                            Name : {}
                            
                            Location : {}
                            
                            LocationID : {}
                            
                            Time : {}
        
                        
                            
                        """.format((name), (str(locationName)), (str(locationID)), (str(timeStamp)))

                        f = open(str(self.emp_id) + ".txt", 'w')
                        f.write(txt_data)
                        f.close()
                        path = (str(self.emp_id))
                        # pdf.output(path + ".pdf")
                        os.chdir("../")

                        return "Saving PDF As.." + str(path) + ".pdf"

                except:
                    print("error")


        else:
            print("Length Zero")
            return "No Record Found"

    # def addFace(self):
    #     result = ft.captureImage(self.emp_id)
    #     return result


def getAll():
    """
    Returns all list of all the employees
    :return:
    """
    data = collection.find()
    return data


def getAttendanceByDate():
    ts = time.time()
    date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    data = list(collection.find({"attendance.date": date}))
    return data
