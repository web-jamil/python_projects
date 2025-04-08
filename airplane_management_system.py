import json
import os


# Flight class: stores information about a specific flight.
class Flight:
    def __init__(self, flight_id, airplane, destination, seats):
        self.flight_id = flight_id
        self.airplane = airplane
        self.destination = destination
        self.seats = seats  # Available seats
        self.passengers = []  # List to store passengers

    def add_passenger(self, passenger_name):
        if self.seats > 0:
            self.passengers.append(passenger_name)
            self.seats -= 1
            print(f"Passenger {passenger_name} added to flight {self.flight_id}. Seats remaining: {self.seats}")
        else:
            print("No seats available on this flight.")

    def view_flight_details(self):
        print(f"Flight ID: {self.flight_id}")
        print(f"Airplane: {self.airplane.model}")
        print(f"Destination: {self.destination}")
        print(f"Seats Available: {self.seats}")
        print("Passengers:")
        for passenger in self.passengers:
            print(f"- {passenger}")


# Airplane class: stores information about an airplane.
class Airplane:
    def __init__(self, airplane_id, model, capacity):
        self.airplane_id = airplane_id
        self.model = model
        self.capacity = capacity  # Maximum seats in the airplane
        self.flights = []  # List to store flights of the airplane

    def add_flight(self, flight_id, destination):
        if len(self.flights) < 3:  # Maximum 3 flights for each airplane
            new_flight = Flight(flight_id, self, destination, self.capacity)
            self.flights.append(new_flight)
            print(f"Flight {flight_id} added to airplane {self.model}.")
        else:
            print(f"Airplane {self.model} can have a maximum of 3 flights.")

    def view_airplane_details(self):
        print(f"Airplane ID: {self.airplane_id}")
        print(f"Model: {self.model}")
        print(f"Capacity: {self.capacity}")
        print("Flights:")
        for flight in self.flights:
            flight.view_flight_details()


# Airplane Management System class: handles all operations and menu options.
class AirplaneManagementSystem:
    def __init__(self):
        self.airplanes = []  # List to store airplanes
        self.load_data()  # Load previously saved data

    def load_data(self):
        """Load airplane and flight data from file"""
        if os.path.exists('airplanes.json'):
            with open('airplanes.json', 'r') as file:
                data = json.load(file)
                for airplane_data in data:
                    airplane = Airplane(airplane_data['airplane_id'], airplane_data['model'], airplane_data['capacity'])
                    self.airplanes.append(airplane)

    def save_data(self):
        """Save airplanes and their flights to a file"""
        airplanes_data = []
        for airplane in self.airplanes:
            airplane_data = {
                'airplane_id': airplane.airplane_id,
                'model': airplane.model,
                'capacity': airplane.capacity,
                'flights': [{'flight_id': flight.flight_id, 'destination': flight.destination, 'seats': flight.seats}
                            for flight in airplane.flights]
            }
            airplanes_data.append(airplane_data)

        with open('airplanes.json', 'w') as file:
            json.dump(airplanes_data, file, indent=4)

    def add_airplane(self, model, capacity):
        airplane_id = len(self.airplanes) + 1
        new_airplane = Airplane(airplane_id, model, capacity)
        self.airplanes.append(new_airplane)
        print(f"Airplane {model} added with ID {airplane_id}.")

    def view_airplanes(self):
        if not self.airplanes:
            print("No airplanes available.")
            return
        for airplane in self.airplanes:
            airplane.view_airplane_details()

    def add_flight(self, airplane_id, flight_id, destination):
        airplane = next((a for a in self.airplanes if a.airplane_id == airplane_id), None)
        if airplane:
            airplane.add_flight(flight_id, destination)
        else:
            print("Airplane not found.")

    def book_seat(self, flight_id, passenger_name):
        for airplane in self.airplanes:
            for flight in airplane.flights:
                if flight.flight_id == flight_id:
                    flight.add_passenger(passenger_name)
                    return
        print("Flight not found.")

    def view_flight_details(self, flight_id):
        for airplane in self.airplanes:
            for flight in airplane.flights:
                if flight.flight_id == flight_id:
                    flight.view_flight_details()
                    return
        print("Flight not found.")

    def menu(self):
        while True:
            print("\n---- Airplane Management System ----")
            print("1. Add Airplane")
            print("2. View All Airplanes")
            print("3. Add Flight to Airplane")
            print("4. Book a Seat for a Passenger")
            print("5. View Flight Details")
            print("6. Exit")
            choice = input("Enter your choice (1-6): ")

            if choice == '1':
                model = input("Enter airplane model: ")
                capacity = int(input("Enter airplane capacity: "))
                self.add_airplane(model, capacity)

            elif choice == '2':
                self.view_airplanes()

            elif choice == '3':
                airplane_id = int(input("Enter airplane ID: "))
                flight_id = int(input("Enter flight ID: "))
                destination = input("Enter flight destination: ")
                self.add_flight(airplane_id, flight_id, destination)

            elif choice == '4':
                flight_id = int(input("Enter flight ID: "))
                passenger_name = input("Enter passenger name: ")
                self.book_seat(flight_id, passenger_name)

            elif choice == '5':
                flight_id = int(input("Enter flight ID: "))
                self.view_flight_details(flight_id)

            elif choice == '6':
                self.save_data()
                print("Data saved. Exiting the system.")
                break

            else:
                print("Invalid choice. Please try again.")


# Main function to start the system
if __name__ == "__main__":
    system = AirplaneManagementSystem()
    system.menu()
