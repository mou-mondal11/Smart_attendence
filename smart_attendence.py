import streamlit as st
import cv2
import numpy as np
import pandas as pd
import face_recognition
import plotly.express as px
import os
from datetime import datetime
import csv
import openpyxl
from openpyxl import Workbook

# Define the Streamlit app
def main():
    st.title("Face Recognition Attendance System")
    st.sidebar.title("Options")

    # File upload
    st.sidebar.subheader("Upload Photos")
    uploaded_files = st.sidebar.file_uploader("Upload Photos", accept_multiple_files=True)

    # Process uploaded files
    if uploaded_files:
        images = []
        classNames = []
        for file in uploaded_files:
            img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                images.append(img)
                classNames.append(os.path.splitext(file.name)[0])

    # Perform face encoding and attendance logic
    def encodingss(images):
        encodelist = []
        for imgA in images:
            img1 = cv2.cvtColor(imgA, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img1)[0]
            encodelist.append(encode)
        return encodelist

    def attendence(name):
        attendance_file = 'Attendance_file.csv'
        file_exists = os.path.isfile(attendance_file)
        with open(attendance_file, 'a', newline='') as f:
            fieldnames = ['Name', 'Date', 'Time', 'Count']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            now = datetime.now()
            date = now.strftime('%Y-%m-%d')
            time = now.strftime('%H:%M:%S')

            updated_entry = False
            attendance_count = 0

            with open(attendance_file, 'r') as file:
                reader = csv.DictReader(file)
                entries = list(reader)

                for entry in entries:
                    if entry['Name'] == name:
                        count = int(entry['Count']) + 1
                        entry.update({'Date': date, 'Time': time, 'Count': str(count)})
                        updated_entry = True
                        attendance_count = count

                if not updated_entry:
                    entries.append({'Name': name, 'Date': date, 'Time': time, 'Count': '1'})
                    attendance_count = 1

            with open(attendance_file, 'w', newline='') as file:
                writer.writeheader()
                writer.writerows(entries)

            st.success(f'{name} is present in the class. Attendance count: {attendance_count}')

    def csv_to_excel(csv_file, excel_file):
        # Read the CSV file using pandas
        df = pd.read_csv(csv_file)

        # Create an Excel writer object
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

        # Write the DataFrame to the Excel file
        df.to_excel(writer, index=False)

        # Save the Excel file
        writer.save()

    # Specify the file paths
    csv_file = 'Attendance_file.csv'
    excel_file = 'Attendance_file.xlsx'

    # Convert the CSV file to Excel
    csv_to_excel(csv_file, excel_file)

    # Open the existing Excel file
    wb = openpyxl.load_workbook('Attendance_file.xlsx')

    # Get the active sheet
    sheet1 = wb.active

    # Create a new sheet
    sheet2 = wb.create_sheet("Sheet2")

    # Add data to the new sheet
    sheet2["A1"] = "Name"
    sheet2["B1"] = "Total Attendance"

    # Save the modified Excel file
    wb.save('attendance.xlsx')


    #define a set to store recognized students
    recognized_students = set()

    # Webcam video capture
    st.sidebar.subheader("Webcam Capture")
    camera_on = st.button("Camera On", key="camera_on")
    stop_camera = False

    if camera_on:
        cap = cv2.VideoCapture(0)
        encode_list_known = encodingss(images)
        camera_off = st.sidebar.button("Camera off", key="camera_off")
        while not stop_camera and cap.isOpened():
            success, img = cap.read()
            if not success:
                continue

            img_s = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # size selection
            img_s = cv2.cvtColor(img_s, cv2.COLOR_BGR2RGB)

            face_current_frame = face_recognition.face_locations(img_s,model="hog")
            encode_current_frame = face_recognition.face_encodings(img_s, face_current_frame)
            for encode_face, face_location in zip(encode_current_frame, face_current_frame):
                matches = face_recognition.compare_faces(encode_list_known, encode_face)
                face_distance = face_recognition.face_distance(encode_list_known, encode_face)
                # print(face_distance)
                match_index = np.argmin(face_distance)
                if matches[match_index]:
                    name = classNames[match_index].upper()
                    if name not in recognized_students:
                        recognized_students.add(name)
                        attendence(name)
                    y1, x2, y2, x1 = face_location
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    #attendence(name)
                    # Display the processed frames
                    st.image(img, channels="BGR")
                    # Stop the loop if Stop button is clicked
                    if camera_off:
                        stop_camera = True
                        break


if __name__ == "__main__":
    main()
data = pd.read_csv('Attendance_file.csv')
st.write('Attendence sheet')

#if st.button("Student Details"):
st.write("Student Details")
tabs = ["Attendence Sheet", "Chart"]

# Display the tabs as radio buttons
selected_tab = st.radio("Attendence", tabs)
# Add content based on the selected tab
if selected_tab == "Attendence Sheet":
    st.header("Attendence Sheet")
    st.dataframe(data)
elif selected_tab == "Chart":
    st.header("Chart")
    fig1 = px.bar(data, x="Name", y="Count", color="Name")
    st.plotly_chart(fig1)
else:
    print("thank you")