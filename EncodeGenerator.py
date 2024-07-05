import cv2
import face_recognition
from face_recognition import face_encodings
import pickle
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://miniprojectfacedetect-default-rtdb.firebaseio.com/",
    "storageBucket": "miniprojectfacedetect.appspot.com"
})

# importing images
folderPath ='Images'
imgPathList = os.listdir(folderPath)
# print(imgPathList) = ['321654.png', '963852.png', '852741.png'] = have to get that img ID
imgList =[]

passengerIDs = []
for path in imgPathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    # print(path)
    # ID = path.split('.')[0] # split the image by '.' and et the 0th index value. Yes that is the syntax, IKR?weird
    # print('ID: ', ID)
    passengerIDs.append(path.split('.')[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(passengerIDs)

# to create encodings; send a list in this function and it will generate encodings that split the list of all encodings
def findEncodings(imagesList):
    encodeList = []
    # loop throgh all image and encode all the img
    for img in imagesList:
        # change the color: BGR TO RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(f"Image dtype: {img.dtype}, Image shape: {img.shape}")
        # Check if the image is in the correct format
        encode = face_recognition.face_encodings(img)[0]
        if encode.any():
            encodeList.append(encode)
        else:
            print("Warning: No face found in the image")

    return encodeList
print("Encoding started")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIDs = [encodeListKnown, passengerIDs]
print(encodeListKnown)
print("Encoding complete")

# generate pickle file:
file = open('EncodeFile.p', "wb")
pickle.dump(encodeListKnownWithIDs, file)
file.close()
print("File saved")