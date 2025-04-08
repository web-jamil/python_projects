# import json
# import os

# # Hall class to represent a hall in the management system
# class Hall:
#     def __init__(self, hall_id, hall_type, capacity, price, is_available=True):
#         self.hall_id = hall_id
#         self.hall_type = hall_type
#         self.capacity = capacity
#         self.price = price
#         self.is_available = is_available

#     def __str__(self):
#         return f"Hall ID: {self.hall_id}, Type: {self.hall_type}, Capacity: {self.capacity}, Price: {self.price}, Available: {'Yes' if self.is_available else 'No'}"


# # Customer class to represent a customer who books a hall
# class Customer:
#     def __init__(self, customer_id, name, contact_info, booked_hall_id=None):
#         self.customer_id = customer_id
#         self.name = name
#         self.contact_info = contact_info
#         self.booked_hall_id = booked_hall_id

#     def __str__(self):
#         return f"Customer ID: {self.customer_id}, Name: {self.name}, Contact Info: {self.contact_info}, Hall Booked: {self.booked_hall_id}"


# # HallManagementSystem class to manage all functionalities related to the halls and customers
# class HallManagementSystem:
#     def __init__(self):
#         self.halls = []  # List to store all halls
#         self.customers = []  # List to store all customers
#         self.load_data()

#     def load_data(self):
#         """Load hall and customer data from JSON files."""
#         if os.path.exists("halls_data.json"):
#             with open("halls_data.json", "r") as file:
#                 data = json.load(file)
#                 for hall_data in data:
#                     hall = Hall(hall_data["hall_id"], hall_data["hall_type"], hall_data["capacity"], hall_data["price"], hall_data["is_available"])
#                     self.halls.append(hall)
        
#         if os.path.exists("customers_data.json"):
#             with open("customers_data.json", "r") as file:
#                 data = json.load(file)
#                 for customer_data in data:
#                     customer = Customer(customer_data["customer_id"], customer_data["name"], customer_data["contact_info"], customer_data["booked_hall_id"])
#                     self.customers.append(customer)

#     def save_data(self):
#         """Save hall and customer data to JSON files."""
#         hall_data = [{"hall_id": hall.hall_id, "hall_type": hall.hall_type, "capacity": hall.capacity, "price": hall.price, "is_available": hall.is_available} for hall in self.halls]
#         customer_data = [{"customer_id": customer.customer_id, "name": customer.name, "contact_info": customer.contact_info, "booked_hall_id": customer.booked_hall_id} for customer in self.customers]
        
#         with open("halls_data.json", "w") as file:
#             json.dump(hall_data, file, indent=4)
        
#         with open("customers_data.json", "w") as file:
#             json.dump(customer_data, file, indent=4)

#     def add_hall(self, hall_type, capacity, price):
#         """Add a new hall to the system."""
#         hall_id = len(self.halls) + 1  # Automatically generate a hall ID based on the count of existing halls
#         new_hall = Hall(hall_id, hall_type, capacity, price)
#         self.halls.append(new_hall)
#         print(f"Hall {hall_id} added successfully.")

#     def remove_hall(self, hall_id):
#         """Remove a hall from the system."""
#         for hall in self.halls:
#             if hall.hall_id == hall_id:
#                 self.halls.remove(hall)
#                 print(f"Hall {hall_id} removed successfully.")
#                 return
#         print("Hall not found.")

#     def display_halls(self):
#         """Display all halls."""
#         if not self.halls:
#             print("No halls available.")
#         else:
#             print("Available Halls:")
#             for hall in self.halls:
#                 print(hall)

#     def check_availability(self):
#         """Display available halls."""
#         available_halls = [hall for hall in self.halls if hall.is_available]
#         if available_halls:
#             print("Available Halls:")
#             for hall in available_halls:
#                 print(hall)
#         else:
#             print("No halls available currently.")

#     def book_hall(self, customer_name, contact_info, hall_id):
#         """Book a hall for a customer."""
#         for hall in self.halls:
#             if hall.hall_id == hall_id:
#                 if hall.is_available:
#                     hall.is_available = False  # Mark the hall as not available
#                     customer_id = len(self.customers) + 1
#                     new_customer = Customer(customer_id, customer_name, contact_info, hall_id)
#                     self.customers.append(new_customer)
#                     print(f"Hall {hall_id} booked successfully for {customer_name}.")
#                     return
#                 else:
#                     print("Hall is already booked.")
#                     return
#         print("Hall not found.")

#     def cancel_booking(self, customer_id):
#         """Cancel a booking for a customer."""
#         for customer in self.customers:
#             if customer.customer_id == customer_id:
#                 hall_id = customer.booked_hall_id
#                 for hall in self.halls:
#                     if hall.hall_id == hall_id:
#                         hall.is_available = True  # Mark the hall as available
#                         self.customers.remove(customer)
#                         print(f"Booking for Customer {customer_id} has been canceled. Hall {hall_id} is now available.")
#                         return
#         print("Customer not found.")

#     def generate_report(self):
#         """Generate a report of the halls and customers."""
#         print("\nHall Management Report:")
#         print("Halls Information:")
#         self.display_halls()
#         print("\nCustomer Information:")
#         for customer in self.customers:
#             print(customer)


# # Hall Management System with User Interface
# class HallManagementUI:
#     def __init__(self):
#         self.system = HallManagementSystem()
#         self.run()

#     def display_menu(self):
#         """Display the menu to the user."""
#         print("\nHall Management System")
#         print("1. Add Hall")
#         print("2. Remove Hall")
#         print("3. Display All Halls")
#         print("4. Check Hall Availability")
#         print("5. Book Hall")
#         print("6. Cancel Booking")
#         print("7. Generate Report")
#         print("8. Exit")

#     def get_choice(self):
#         """Get the user's menu choice."""
#         while True:
#             try:
#                 choice = int(input("Enter your choice (1-8): "))
#                 if choice in range(1, 9):
#                     return choice
#                 else:
#                     print("Invalid choice. Please choose a number between 1 and 8.")
#             except ValueError:
#                 print("Invalid input. Please enter a valid number.")

#     def handle_choice(self, choice):
#         """Handle the user's menu choice."""
#         if choice == 1:  # Add Hall
#             hall_type = input("Enter hall type (Conference/Marriage/Party): ")
#             capacity = int(input("Enter hall capacity: "))
#             price = float(input("Enter hall price per day: "))
#             self.system.add_hall(hall_type, capacity, price)

#         elif choice == 2:  # Remove Hall
#             hall_id = int(input("Enter hall ID to remove: "))
#             self.system.remove_hall(hall_id)

#         elif choice == 3:  # Display All Halls
#             self.system.display_halls()

#         elif choice == 4:  # Check Hall Availability
#             self.system.check_availability()

#         elif choice == 5:  # Book Hall
#             customer_name = input("Enter customer name: ")
#             contact_info = input("Enter customer contact info: ")
#             hall_id = int(input("Enter hall ID to book: "))
#             self.system.book_hall(customer_name, contact_info, hall_id)

#         elif choice == 6:  # Cancel Booking
#             customer_id = int(input("Enter customer ID to cancel booking: "))
#             self.system.cancel_booking(customer_id)

#         elif choice == 7:  # Generate Report
#             self.system.generate_report()

#         elif choice == 8:  # Exit
#             self.system.save_data()
#             print("Exiting the system. All data has been saved.")
#             exit()

#     def run(self):
#         """Run the Hall Management System."""
#         while True:
#             self.display_menu()
#             choice = self.get_choice()
#             self.handle_choice(choice)


# if __name__ == "__main__":
#     HallManagementUI()
