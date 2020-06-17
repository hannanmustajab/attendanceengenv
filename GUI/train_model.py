import cv2
import numpy as np
from PIL import Image
import os

# Path for face image database
# path = 'train_data'
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml");
# # function to get the images and label data
imagePaths = [os.path.join('train_data', f) for f in os.listdir('train_data')]
try:
    imagePaths.remove('train_data/.DS_Store')
except:
    pass
faceSamples = []
ids = []
print(os.getcwd())


def getImagesAndLabels(path):
    print(os.getcwd())
    for imagePath in imagePaths:
        images = [os.path.join(imagePath, f) for f in os.listdir(imagePath)]
        for image in images:
            PIL_img = Image.open(image).convert('L')  # grayscale
            img_numpy = np.array(PIL_img, 'uint8')
            id = int(os.path.split(image)[0].split("/")[1])
            faces = detector.detectMultiScale(img_numpy)
            for (x, y, w, h) in faces:
                faceSamples.append(img_numpy[y:y + h, x:x + w])
                ids.append(id)
    return faceSamples, ids


def TrainModel():
    print("######################################################")
    print(os.getcwd())
    print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    print(os.getcwd())
    path = 'train_data'
    print(os.getcwd())
    faces, ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))
    # Save the model into trainer/trainer.yml
    recognizer.write('trainer/trainer.yml')
    # Print the numer of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))

