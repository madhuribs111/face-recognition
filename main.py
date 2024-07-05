import cv2
import os
import pickle

import cvzone
import numpy as np
import face_recognition

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://miniprojectfacedetect-default-rtdb.firebaseio.com/",
    "storageBucket": "miniprojectfacedetect.appspot.com"
})

bucket = storage.bucket()
# 0 is webcam
capture = cv2.VideoCapture(0)

if not capture.isOpened():
    print("Error: Could not open webcam.")
    exit()
# width
capture.set(3, 640)
# height
capture.set(4, 480)
# the compleet img size: 1280/720
imgBackground = cv2.imread('Resources/background.png')
# Loading mode images into a list
folderModePath ='Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList =[]
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
print(len(imgModeList))

# Load the encoding file
print("Loading encoded file...")
file =open("EncodeFile.p", 'rb')
encodeListKnownWithIDs = pickle.load(file)
# extract list into two parts: paasengerIDs, encodeListKnown
file.close()
encodeListKnown, passengerIDs = encodeListKnownWithIDs
#print(passengerIDs)
print("Encoded file loaded")

modeType = 0
# only download the image from the database for one time in the first iteration
counter  = 0
id = -1
while True:
    success, img = capture.read()
    if not success:
        print("Failed to capture image. Exiting.")
        break
    # scale it down to 1/4 th of the image
    imgS = cv2.resize(img,(0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrFrame = face_recognition.face_locations(imgS)
    # find the small image imgS's encodings
    encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)

    # take webcam and place it on the bg:
    imgBackground[162:162 + 480, 55:55 + 640] = img # left side of the bg
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType] # right side of the bg
    # the ability to change the modes: marked, already marked...


    for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDist = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print("Matches: ", matches)
        # print("Face Disatance: ", faceDist)
        matchIndex = np.argmin(faceDist)
        if matchIndex:
            print("Match Index: ", matchIndex)  # if the first array value is matches, match index : 0
        if not matchIndex:
            print("No match index")

        if matches[matchIndex]:
            # print("Known face detected", studentIDs[matchIndex])
            # bbox: bounding box
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1* 4, x2 * 4, y2 * 4,x1*4 # multiply by 4 because we have scaled it to 1/4th
            # out face is actually not starting from (0,0). there are some x and y values we have to move: bbox
            bbox = 55 + x1, 162 +y1, x2-x1, y2-y1
            imageBackground = cvzone.cornerRect(
                imgBackground,
                bbox,
                # (200, 200, 300, 200),  # The position and dimensions of the rectangle (x, y, width, height)
                l=30,  # Length of the corner edges
                t=5,  # Thickness of the corner edges
                rt=0,  # Thickness of the rectangle
                colorR=(255, 0, 255),  # Color of the rectangle
                colorC=(0, 255, 0)  # Color of the corner edges)
            )
            id = passengerIDs[matchIndex]
            # print(id)
            if counter == 0:
                counter=1
                modeType = 1
    if counter != 0:

        if counter ==1:
            # download/ get the data
            passengerInfo = db.reference(f'Passengers/{id}').get() # get all info of the id
            print(passengerInfo)
            # get the image from the storage
            blob = bucket.get_blob(f'Images/{id}.png')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgPassenger = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
            # update the attendance
            ref = db.reference(f'Passengers/{id}')
       #     studentInfo['total_attendance'] +=1
        #    ref.child('total_attendance').set(studentInfo['total_attendance'])

        if 30<counter<40:
            modeType = 2
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]  # right side of the bg

        if counter<=30:
            # put in the correct location of the bg:


            cv2.putText(imgBackground, str(passengerInfo['class']),
                        (1040, 555),  # position of class
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 1)
            cv2.putText(imgBackground, str(passengerInfo['flight']),
                        (1000, 500),  # position of flight
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 1)
            cv2.putText(imgBackground, str(passengerInfo['departure']),
                        (840,622),  # posiition of that total attendance placeholder
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,0,0), 1)
            cv2.putText(imgBackground, str(passengerInfo['arrival']),
                        (1076,620),  # posiition of that total attendance placeholder
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,0,0), 1)


            (w, h), _ =cv2.getTextSize(passengerInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1) # width and height of the text
            offset = (414-w)//2
            cv2.putText(imgBackground, str(passengerInfo['name']),
                        (808 + offset, 445),  # posiition of that total attendance placeholder
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50,50,50), 1)

            imgBackground[175: 175+216, 909: 909+216] = imgPassenger

        counter +=1

            # after it shows "marked":
        if counter >=40:
            counter = 0
            modeType = 0
            imgPassenger = []
            passengerInfo = []
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]  # right side of the bg

    # cv2.imshow("Web cam", img)
    cv2.imshow("Face recog background", imgBackground)
    cv2.waitKey(1)