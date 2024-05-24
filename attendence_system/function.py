import base64
from io import BytesIO
import os
import pickle
import secrets
import shutil
import string
import time
from click import FileError
from flask import flash, request, send_file
import numpy as np
import pandas as pd
from attendence_system import db
import cv2
import face_recognition
from attendence_system import stop_task
from takeattedance import take_attendance

cam_act = False




def delete_all_files(directory_path):
    try:
        # Delete the folder and all its contents
        shutil.rmtree(directory_path)
        print(f"Folder '{directory_path}' and its contents deleted successfully.")
    except OSError as e:
        print(f"Error: {directory_path} : {e.strerror}")

            
            
def capture_images():
    capture_folder = 'captured_images'
    delete_all_files(capture_folder)
    if not os.path.exists(capture_folder):
        os.makedirs(capture_folder)
    camera = cv2.VideoCapture(0)
    
    images_captured = 0
    while images_captured < 3:
        ret, frame = camera.read()
        if not ret:
            break
        image_path = os.path.join(capture_folder, f'image_{images_captured+1}.jpg')
        cv2.imwrite(image_path, frame)
        images_captured += 1
        preview_image(image_path, images_captured)

        # Wait for some time before capturing the next image
        time.sleep(0.1)
    camera.release()
    camera_active = False
    return 'Images captured successfully!'


def get_cameras():
    # Get the list of available cameras
    request_camera_permission()
    cameras = []
    for i in range(10):  # Check up to 10 camera devices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                cameras.append(f"Camera {i}")
            cap.release()
    print(cameras)
    return cameras


def preview_image(image_path, index):
    try:  
        with open(image_path, 'rb') as file:
            img_base64 = base64.b64encode(file.read()).decode('utf-8')

        # Update the preview div with the captured image
        javascript_code = f'document.getElementById("image_preview_{index}").src = "data:image/jpeg;base64,{img_base64}";'
    except FileError as  e:
                print(f'{e}', "danger")
    return javascript_code




def stop_camera(camera_active):
    global cam_act
    cam_act = camera_active
    return camera_active 
    
    
    
def generate_frames(camera_active):
    global cam_act 
    cam_act = camera_active
    cameras_list= get_cameras()
    camera=cv2.VideoCapture(0)
    while camera_active:
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            try:
                detector=cv2.CascadeClassifier(r'data\haarcascade_frontalface_default.xml')
                # eye_cascade = cv2.CascadeClassifier('Haarcascades/haarcascade_eye.xml')
                faces=detector.detectMultiScale(frame,1.1,7)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                #Draw the rectangle around each face
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]
                    # eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
                    # for (ex, ey, ew, eh) in eyes:
                    #     cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f'{e}', "danger")  
                
                
                

def get_connected_cameras():
    # Create an empty list to store camera devices
    cameras = []

    # Enumerate through camera devices
    for i in range(10):  # Check up to 10 devices, adjust if needed
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if not cap.isOpened():
            break

        # Get camera properties
        camera_info = {
            "index": i,
            "name": f"Camera {i}",
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        }

        cameras.append(camera_info)

        # Release the camera
        cap.release()

    return cameras

def request_camera_permission():
    # Access the camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open camera. Permission denied.")
        return False

    # Release the camera
    cap.release()
    return None
    

def find_file(file_name, search_path="."):
    """
    Find the file path by searching for the file name within the specified directory
    or its subdirectories.

    Args:
        file_name (str): The name of the file to search for.
        search_path (str): The directory path to search in. Defaults to the current directory.

    Returns:
        str: The absolute path to the file if found, or None if not found.
    """
    # Iterate over the directory and its subdirectories
    for root, dirs, files in os.walk(search_path):
        # Check if the file name is in the list of files in the current directory
        if file_name in files:
            # Return the absolute path to the file
            return os.path.join(root, file_name)
    # File not found
    return None

def rename_images(directory_path, new_name):
    # Counter for generating unique names
    count = 0
    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        current_path = os.path.join(directory_path, filename)
        # Check if the path is a file
        if os.path.isfile(current_path):
            # Get the file extension
            file_extension = os.path.splitext(filename)[1]
            # Generate the new filename
            new_filename = f"{new_name}_{count}{file_extension}"
            # Construct the new path
            new_path = os.path.join(directory_path, new_filename)
            # Rename the file
            os.rename(current_path, new_path)
            # Increment the counter
            count += 1
            
            
def FaceEncode(image_files, directory_path):
    serialized_encoding_list = []
    for file_name in image_files:
        file_path = os.path.join(directory_path, file_name)
        if os.path.exists(file_path):
            image = face_recognition.load_image_file(file_path)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                face_encoding = face_encodings[0]
                print(face_encoding.shape)
                # print("this is face encoding", face_encoding)
                serialized_encoding = pickle.dumps(face_encoding)    
                # print("this is serialized_encoding", serialized_encoding)     
            else:
                flash(f"No face found in {file_name}", "warning")
        else:
            flash(f"File {file_name} not found!", "danger")
        serialized_encoding_list.append(serialized_encoding)
    return serialized_encoding_list



def compare_face_encodings(list1, list2):
    try:
        deserialized_encoding_1 = pickle.loads(list1)
        deserialized_encoding_2 = pickle.loads(list2)
        
        if np.array_equal(deserialized_encoding_1,deserialized_encoding_2):
            print("The serialized encodings are the same")
        else:
            print("The serialized encodings are different")
    except Exception as e :
        print(e)
        
        
def generate_password(length=6):
    # Define the characters to be used in the password
    characters = string.ascii_letters + string.digits

    # Generate the password
    password = ''.join(secrets.choice(characters) for i in range(length))
    
    return password



def background_task():
    """Function that runs a background task"""
    while not stop_task.is_set():
        take_attendance()
        time.sleep(10)  # Simulate a long-running task
        print("Background task completed")
        
        
        
def download_excel(attendance_data):
    df = pd.DataFrame(attendance_data)

    # Create a BytesIO buffer to save the Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')

    # Set the buffer's position to the start
    output.seek(0)

    # Send the file to the user
    return send_file(output, download_name='attendance.xlsx', as_attachment=True)