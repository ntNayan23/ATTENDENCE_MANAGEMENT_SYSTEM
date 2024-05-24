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

    try:
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
    except Exception as e:
        print(f"Error loading face encodings: {e}")

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
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame")
            break

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        if process_this_frame:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                face_id = None

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    face_id = known_face_names[best_match_index]

                    if face_id:
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

                        subquery_result = session.execute(select(subquery)).fetchone()
                        if subquery_result:
                            person_id = subquery_result.person_id
                            is_employee = subquery_result.is_employee
                            if is_employee:
                                name_query = select(Employee.name).where(Employee.id == person_id)
                            else:
                                name_query = select(Student.name).where(Student.id == person_id)

                            result = session.execute(name_query).fetchone()
                            if result:
                                name = result[0]
                                current_date = datetime.now().date()
                                current_time = datetime.now().time()

                                attendance_exists_query = select(Attendance).where(
                                    and_(
                                        (Attendance.employee_id == person_id if is_employee else Attendance.student_id == person_id),
                                        Attendance.date == current_date
                                    )
                                )

                                attendance_record = session.execute(attendance_exists_query).fetchone()

                                if attendance_record:
                                    attendance_id = attendance_record[0].id
                                    intime = attendance_record[0].in_time
                                    intime_datetime = datetime.combine(datetime.now().date(), intime)
                                    current_datetime = datetime.combine(datetime.now().date(), current_time)
                                    if current_datetime >= (intime_datetime + timedelta(minutes=1)):
                                        attendance_update = (
                                            update(Attendance)
                                            .where(Attendance.id == attendance_id)
                                            .values(out_time=current_time)
                                        )
                                        session.execute(attendance_update)
                                        session.commit()
                                        print("Attendance record updated with out time")
                                    else:
                                        print("1 minute not elapsed since intime, skipping out time update")
                                else:
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
                                print("No record found for the person ID")
                        else:
                            print("No person ID found for face ID")
                    else:
                        print("No matching face ID found")

                face_names.append(name.split()[0])

        process_this_frame = not process_this_frame

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, str(name), (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    session.close()

if __name__ == "__main__":
    take_attendance()
