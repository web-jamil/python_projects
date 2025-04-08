import os
import json
from datetime import datetime


# Student Class
class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name

    def __str__(self):
        return f"{self.student_id}. {self.name}"


# Attendance Class
class Attendance:
    def __init__(self):
        self.attendance_data = {}  # Stores attendance data with dates as keys

    def mark_attendance(self, student, status):
        """Mark the attendance of a student on the current date."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        if current_date not in self.attendance_data:
            self.attendance_data[current_date] = {}

        self.attendance_data[current_date][student.student_id] = status
        print(f"Attendance for {student.name} on {current_date} marked as {status}.")

    def view_attendance(self):
        """View the attendance record of all students."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        if current_date not in self.attendance_data:
            print("No attendance data for today.")
            return

        print(f"\nAttendance for {current_date}:")
        for student_id, status in self.attendance_data[current_date].items():
            print(f"Student ID: {student_id}, Status: {status}")

    def save_attendance(self):
        """Save attendance data to a file."""
        with open('attendance.json', 'w') as file:
            json.dump(self.attendance_data, file, indent=4)

    def load_attendance(self):
        """Load attendance data from a file."""
        if os.path.exists('attendance.json'):
            with open('attendance.json', 'r') as file:
                self.attendance_data = json.load(file)


# Attendance System Class
class AttendanceSystem:
    def __init__(self):
        self.students = []  # List of all students
        self.attendance = Attendance()  # Attendance object to manage attendance
        self.load_data()  # Load previous data (students and attendance) if any

    def load_data(self):
        """Load students and attendance data."""
        self.attendance.load_attendance()

        if os.path.exists('students.json'):
            with open('students.json', 'r') as file:
                data = json.load(file)
                for student_data in data:
                    student = Student(student_data['student_id'], student_data['name'])
                    self.students.append(student)

    def save_data(self):
        """Save students and attendance data."""
        with open('students.json', 'w') as file:
            students_data = [{'student_id': student.student_id, 'name': student.name} for student in self.students]
            json.dump(students_data, file, indent=4)

        self.attendance.save_attendance()

    def add_student(self, name):
        """Add a new student to the system."""
        student_id = len(self.students) + 1
        new_student = Student(student_id, name)
        self.students.append(new_student)
        print(f"Student {name} added with ID {student_id}.")

    def view_students(self):
        """View all registered students."""
        if not self.students:
            print("No students registered yet.")
            return

        print("\nList of Students:")
        for student in self.students:
            print(student)

    def mark_student_attendance(self, student_id, status):
        """Mark attendance for a specific student."""
        student = next((s for s in self.students if s.student_id == student_id), None)
        if student:
            self.attendance.mark_attendance(student, status)
        else:
            print("Student not found.")

    def view_all_attendance(self):
        """View attendance records for all students for the current day."""
        self.attendance.view_attendance()

    def generate_report(self):
        """Generate a report of attendance for the current date."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        if current_date not in self.attendance.attendance_data:
            print(f"No attendance data for {current_date}.")
            return

        print(f"\nAttendance Report for {current_date}:")
        for student_id, status in self.attendance.attendance_data[current_date].items():
            student = next((s for s in self.students if s.student_id == student_id), None)
            if student:
                print(f"Student ID: {student.student_id}, Name: {student.name}, Status: {status}")


# User Interface (UI) for Attendance System
class AttendanceSystemUI:
    def __init__(self):
        self.system = AttendanceSystem()
        self.run()

    def display_menu(self):
        """Display the main menu."""
        print("\nStudent Attendance Management System")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Mark Attendance")
        print("4. View Today's Attendance")
        print("5. Generate Attendance Report")
        print("6. Exit")

    def get_choice(self):
        """Get the user's menu choice."""
        while True:
            try:
                choice = int(input("Enter your choice (1-6): "))
                if 1 <= choice <= 6:
                    return choice
                else:
                    print("Invalid choice. Please enter a number between 1 and 6.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def handle_choice(self, choice):
        """Handle the user's menu choice."""
        if choice == 1:  # Add a Student
            name = input("Enter student name: ")
            self.system.add_student(name)

        elif choice == 2:  # View All Students
            self.system.view_students()

        elif choice == 3:  # Mark Attendance
            self.system.view_students()
            student_id = int(input("Enter student ID to mark attendance: "))
            status = input("Enter attendance status (Present/Absent): ").lower()
            if status in ['present', 'absent']:
                self.system.mark_student_attendance(student_id, status)
            else:
                print("Invalid status. Please enter 'Present' or 'Absent'.")

        elif choice == 4:  # View Today's Attendance
            self.system.view_all_attendance()

        elif choice == 5:  # Generate Attendance Report
            self.system.generate_report()

        elif choice == 6:  # Exit
            self.system.save_data()
            print("Data saved. Exiting the system.")
            exit()

    def run(self):
        """Run the main loop of the attendance system."""
        while True:
            self.display_menu()
            choice = self.get_choice()
            self.handle_choice(choice)


if __name__ == "__main__":
    AttendanceSystemUI()
