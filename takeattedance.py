# import os
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.automap import automap_base

# # Step 1: Locate the SQLite file
# # Replace 'path/to/your/database.db' with the actual path to your SQLite database file
# db_path = r'D:\project\ATTENDENCE_MANAGEMENT_SYSTEM\instance\AMS.db'

# # Check if the file exists
# if not os.path.exists(db_path):
#     print("SQLite file not found.")
#     exit()

# # Step 2: Connect to the SQLite database using SQLAlchemy
# engine = create_engine(f"sqlite:///{db_path}")

# # Step 3: Form a select query
# select_query = text("""
#     SELECT * FROM branch_name
# """)

# # Step 4: Execute the query and process the results
# Session = sessionmaker(bind=engine)
# session = Session()

# try:
#     result = session.execute(select_query)
#     rows = result.fetchall()

#     # Print the retrieved data
#     for row in rows:
#         print(row)

# except Exception as e:
#     print(f"An error occurred: {e}")

# finally:
#     session.close()
import os
import cv2
import numpy as np
import sqlite3
import face_recognition

def check_attendance():
    # Set the path to the SQLite database file
    try:
        # Retrieve serialized face encodings from the database
        cursor.execute("SELECT * FROM face_encoding")
        stored_face_encodings = cursor.fetchall()
        print("working")
        # Deserialize the retrieved face encodings
        known_encodings = [np.frombuffer(face[1], dtype=np.float64) for face in stored_face_encodings]

        # Capture a frame using OpenCV
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()

        # Convert the frame from BGR to RGB (OpenCV uses BGR by default)
        rgb_frame = frame[:, :, ::-1]

        # Detect faces in the captured frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Compare the captured face encodings with the stored face encodings
        for face_encoding in face_encodings:
            # Compare the captured face encoding with each known encoding
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            
            # Check if any match is found
            if True in matches:
                # Retrieve the corresponding information associated with the matched face encoding from the database
                index = matches.index(True)
                matched_face = stored_face_encodings[index]
                
                # Check if the matched face belongs to an employee or a student
                if matched_face[2]:
                    cursor.execute("SELECT * FROM employee WHERE id=?", (matched_face[2],))
                    employee = cursor.fetchone()
                    print("Matched Employee:", employee[1])
                    # Perform additional actions for attendance recording, etc., if needed
                elif matched_face[3]:
                    cursor.execute("SELECT * FROM student WHERE id=?", (matched_face[3],))
                    student = cursor.fetchone()
                    print("Matched Student:", student[1])
                    # Perform additional actions for attendance recording, etc., if needed

        # Release the capture device
        cap.release()

        # Close the database connection
        conn.close()

        
    except Exception as e:
        print(e) 
# Call the function to check attendance
if __name__ == '__main__':
    try:
        db_path = r'D:\project\ATTENDENCE_MANAGEMENT_SYSTEM\instance\AMS.db'

        # Check if the file exists
        if not os.path.exists(db_path):
            print("SQLite file not found.")
            exit()

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except Exception as e:
        print(e)
    check_attendance()
