from datetime import datetime, timedelta
import os
import pickle
import numpy as np
import cv2
import face_recognition
from sqlalchemy import and_, case, create_engine, MetaData, Table, insert, select, update
from sqlalchemy.orm import sessionmaker
from attendence_system.model import Attendance, Employee, FaceEncoding, Student
from attendence_system import stop_task

def take_attendance():
    # Connect to the SQLite database
    db_path = r'D:\project\ATTENDENCE_MANAGEMENT_SYSTEM\instance\AMS.db'
    # Check if the file exists
    if not os.path.exists(db_path):
        print("SQLite file not found.")
        exit()

    db_path = r'sqlite:///D:/project/ATTENDENCE_MANAGEMENT_SYSTEM/instance/AMS.db'
    engine = create_engine(db_path)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Reflect the existing database schema
    metadata = MetaData()
    metadata.reflect(bind=engine)
    face_encoding_table = Table('face_encoding', metadata, autoload_with=engine)


    known_face_encodings = []
    known_face_names = []
    stored_face_encodings_list = session.query(FaceEncoding).all()

    for face_encoding in stored_face_encodings_list:
        try:
            encoding_data = face_encoding.encoding
            encoding = pickle.loads(encoding_data)
            if len(encoding) == 128:
                known_face_encodings.append(encoding)
                known_face_names.append(face_encoding.id if face_encoding.employee_id else face_encoding.student_id)
            else:
                print(f"Unexpected encoding length for ID {face_encoding.id}: {len(encoding)}")
        except Exception as e:
            print(f"Error deserializing encoding data for ID {face_encoding.id}: {e}")

    print("Loaded known face encodings:", known_face_encodings)
    print("Loaded known face names:", known_face_names)
    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    while not stop_task.is_set():
        # Grab a single frame of video
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame")
            break

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                name = str(name)
                print(f"Name to be displayed: {name}")
                # Use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    face_id = known_face_names[best_match_index]
                # Step 1: Create a subquery tsubquery = (
                    subquery = (
                                select(
                                    case(
                                        (FaceEncoding.employee_id != None, FaceEncoding.employee_id),
                                        else_=FaceEncoding.student_id
                                    ).label('person_id'),
                                    case(
                                        (FaceEncoding.employee_id != None, True),
                                        else_=False
                                    ).label('is_employee')
                                ).where(FaceEncoding.id == face_id)
                            ).subquery()

                # Step 2: Fetch the subquery result
                subquery_result = session.execute(select(subquery)).fetchone()
                if subquery_result:
                    person_id = subquery_result.person_id
                    is_employee = subquery_result.is_employee

                    # Step 3: Use the obtained ID to get the name from the Employee or Student table
                    if is_employee:
                        name_query = select(Employee.name).where(Employee.id == person_id)
                    else:
                        name_query = select(Student.name).where(Student.id == person_id)

                    result = session.execute(name_query).fetchone()

                    if result:
                        name = result[0]  # Assuming the result is a tuple with the name as the first element
                        print("Name:", name)

                        # Check if an attendance record already exists for the current date
                        current_date = datetime.now().date()
                        current_time = datetime.now().time()

                        attendance_exists_query = select(Attendance).where(
                            and_(
                                (Attendance.employee_id == person_id if is_employee else Attendance.student_id == person_id),
                                Attendance.date == current_date
                            )
                        )

                        attendance_record = session.execute(attendance_exists_query).fetchone()
                        print(attendance_record)

                        if attendance_record:
                            # Update the out_time for the existing attendance record
                            print("Attendance record found:", attendance_record)
                            attendance_id = attendance_record[0].id  
                            intime = attendance_record[0].in_time  # Accessing the first element and then in_time
                            intime_datetime = datetime.combine(datetime.now().date(), intime)
                            current_datetime = datetime.combine(datetime.now().date(), current_time)
                            if current_datetime >= (intime_datetime + timedelta(minutes=1)):
                                # Update the out_time for the existing attendance record
                                attendance_update = (
                                    update(Attendance)
                                    .where(Attendance.id == attendance_id)
                                    .values(out_time=current_time)
                                )
                                session.execute(attendance_update)
                                session.commit()
                                print("Attendance record updated with out time")
                            else:
                                print("20 minutes not elapsed since intime, skipping out time update")
                        else:
                            # Insert a new attendance record
                            attendance_insert = insert(Attendance).values(
                                employee_id=person_id if is_employee else None,
                                student_id=person_id if not is_employee else None,
                                date=current_date,
                                in_time=current_time
                            )
                            session.execute(attendance_insert)
                            session.commit()
                            print("Attendance record inserted")
                    else:
                        print("No record found")
                else:
                    print("No record found")

                # Close the session
                session.close()

                face_names.append(name.split()[0])

        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, str(name), (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        # cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    # Close the database connection


