from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter as tki
import threading
import cv2
import time
import Employee
import os
from train_model import TrainModel

class MarkingAttendance:

    def function_TI(self):
        self.thread = threading.Thread(target=self.TI_videoLoop, args=())
        self.thread.start()

    def TI_videoLoop(self):
        os.chdir("train_data")

        def checkDirectory(emp_id):
            """
            Check if a directory for that employee id exists. If it exits then change directory and save the new images to it.
            Else create a directory,change to it and store in it.
            :return:
            """
            if str(emp_id) in os.listdir(os.getcwd()):
                os.chdir(str(emp_id))
                return "Changed Directory to " + str(emp_id)
            else:
                os.mkdir(str(emp_id))
                os.chdir(str(emp_id))
                return "Creating a new directory"

        def captureImage(emp_id):
            i = 0
            checkDirectory(emp_id)
            while i < 50:
                # raw_input('Press Enter to capture')
                return_value, self.frame = self.vs.read()
                gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                faces = faceCascade.detectMultiScale(
                    gray,
                    scaleFactor=1.3,
                    minNeighbors=3,
                    minSize=(30, 30)
                )
                for (x, y, w, h) in faces:
                    cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                height, width = self.frame.shape[:2]

                for (x, y, w, h) in faces:
                    r = max(w, h) / 2
                    centerx = x + w / 2
                    centery = y + h / 2
                    nx = int(centerx - r)
                    ny = int(centery - r)
                    nr = int(r * 2)

                    faceimg = self.frame[ny:ny + nr, nx:nx + nr]
                    lastimg = cv2.resize(faceimg, (512, 512))
                    status = cv2.imwrite(str(emp_id) + '_' + str(i) + '.jpg', lastimg)
                if self.panel is None:
                    self.panel = tki.Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx=10, pady=10)

                else:
                    self.panel.configure(image=image)
                    self.panel.image = image

                print("[INFO] Found {0} Faces!".format(len(faces)))
                i += 1
                self.welcomeLabel.config(text=f'Took {i} images, found {len(faces)} faces', bg='lightgreen')
                self.btn1.config(text="Close", command=self.onClose)

        captureImage(self.empID)
        self.finalLabel = tki.Label(text=f'Please wait, Training the model now. ', bg="lightgreen")
        self.finalLabel.pack(side="bottom", fill="both", padx=10,
                               pady=10)
        os.chdir('../../')
        import train_model
        train_model.TrainModel()
        
        self.finalLabel = tki.Label(text=f'Images successfully trained for {self.name}, Emp. Id:- {self.empID}', bg="lightgreen")
        self.finalLabel.pack(side="bottom", fill="both", padx=10,
                               pady=10)

    def onClose(self):
        print("[INFO] closing...")
        self.stopEvent.set()
        self.root.quit()
        self.vs.release()

    def next_function(self):
        self.empID = self.enter_id.get()
        employee = Employee.Employee(self.empID)
        # print(employee.fullName())
        self.name = employee.fullName()
        self.enter_id.pack_forget()
        self.enterLabel.pack_forget()
        self.welcomeLabel = tki.Label(text=f'Welcome {self.name}', bg="lightgreen")
        self.welcomeLabel.pack(side="bottom", fill="both", expand="yes", padx=10,
                         pady=10)
        self.btn1.config(text="Train", command=self.function_TI)

    def initial(self):
        self.enterLabel = tki.Label(text=f'Enter ID', bg="lightblue")
        self.enterLabel.pack(fill="both", expand="yes", padx=10,
                               pady=10)
        self.enter_id = tki.Entry(self.root)
        self.enter_id.pack(fill="both", expand="yes", padx=10,
                        pady=10)
        self.btn1 = tki.Button(self.root, text='Proceed', command=self.next_function)
        self.btn1.pack(side="bottom", fill="both", expand="yes", padx=10,
                       pady=10)
    def __init__(self, vs):
        self.vs = vs
        self.frame = None
        self.thread = None
        self.stopEvent = None

        self.root = tki.Tk()
        self.panel = None

        self.vs.set(3, 480)
        self.vs.set(4, 480)
        self.stopEvent = threading.Event()

        self.initial()

        self.root.wm_title("Face Recognition")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)


print("[INFO] warming up camera...")
vs = cv2.VideoCapture(0)
time.sleep(2.0)

pba = MarkingAttendance(vs)
pba.root.mainloop()