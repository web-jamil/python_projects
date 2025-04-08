import json
import os

# Candidate class represents a candidate in the election
class Candidate:
    def __init__(self, candidate_id, name, party_name):
        self.candidate_id = candidate_id
        self.name = name
        self.party_name = party_name
        self.vote_count = 0

    def __str__(self):
        return f"{self.candidate_id}. {self.name} ({self.party_name}) - Votes: {self.vote_count}"

    def increment_vote(self):
        self.vote_count += 1


# Voter class to store voter information
class Voter:
    def __init__(self, voter_id, name, age, voted=False):
        self.voter_id = voter_id
        self.name = name
        self.age = age
        self.voted = voted

    def __str__(self):
        return f"{self.voter_id}. {self.name}, Age: {self.age} - Voted: {'Yes' if self.voted else 'No'}"

    def vote(self):
        self.voted = True


# EVM (Electronic Voting Machine) class to manage the election system
class EVM:
    def __init__(self):
        self.candidates = []  # List of candidates
        self.voters = []  # List of voters
        self.load_data()  # Load existing data if available

    def load_data(self):
        """Load candidates and voters data from JSON files."""
        if os.path.exists("candidates.json"):
            with open("candidates.json", "r") as file:
                data = json.load(file)
                for candidate_data in data:
                    candidate = Candidate(candidate_data["candidate_id"], candidate_data["name"], candidate_data["party_name"])
                    candidate.vote_count = candidate_data["vote_count"]
                    self.candidates.append(candidate)

        if os.path.exists("voters.json"):
            with open("voters.json", "r") as file:
                data = json.load(file)
                for voter_data in data:
                    voter = Voter(voter_data["voter_id"], voter_data["name"], voter_data["age"], voter_data["voted"])
                    self.voters.append(voter)

    def save_data(self):
        """Save the candidates and voters data to JSON files."""
        candidates_data = [{"candidate_id": candidate.candidate_id, "name": candidate.name, "party_name": candidate.party_name, "vote_count": candidate.vote_count} for candidate in self.candidates]
        voters_data = [{"voter_id": voter.voter_id, "name": voter.name, "age": voter.age, "voted": voter.voted} for voter in self.voters]
        
        with open("candidates.json", "w") as file:
            json.dump(candidates_data, file, indent=4)
        
        with open("voters.json", "w") as file:
            json.dump(voters_data, file, indent=4)

    def add_candidate(self, name, party_name):
        """Add a new candidate to the election."""
        candidate_id = len(self.candidates) + 1
        new_candidate = Candidate(candidate_id, name, party_name)
        self.candidates.append(new_candidate)
        print(f"Candidate {name} from {party_name} added with ID {candidate_id}.")

    def add_voter(self, name, age):
        """Add a new voter."""
        if age >= 18:
            voter_id = len(self.voters) + 1
            new_voter = Voter(voter_id, name, age)
            self.voters.append(new_voter)
            print(f"Voter {name} added with ID {voter_id}.")
        else:
            print("Voter must be at least 18 years old.")

    def list_candidates(self):
        """Display all available candidates."""
        print("\nCandidates:")
        for candidate in self.candidates:
            print(candidate)

    def list_voters(self):
        """Display all registered voters."""
        print("\nVoters:")
        for voter in self.voters:
            print(voter)

    def vote(self, voter_id, candidate_id):
        """Cast a vote for a candidate."""
        # Check if the voter exists
        voter = next((v for v in self.voters if v.voter_id == voter_id), None)
        if not voter:
            print("Voter not found.")
            return
        
        # Check if the voter has already voted
        if voter.voted:
            print("This voter has already cast their vote.")
            return
        
        # Check if the candidate exists
        candidate = next((c for c in self.candidates if c.candidate_id == candidate_id), None)
        if not candidate:
            print("Candidate not found.")
            return
        
        # Cast the vote
        candidate.increment_vote()
        voter.vote()  # Mark the voter as having voted
        print(f"Vote cast successfully for {candidate.name} from {candidate.party_name}.")
    
    def show_results(self):
        """Show the election results."""
        print("\nElection Results:")
        for candidate in self.candidates:
            print(f"{candidate.name} ({candidate.party_name}): {candidate.vote_count} votes")
    
    def generate_report(self):
        """Generate a complete report."""
        self.show_results()
        print("\nVoter Status Report:")
        self.list_voters()


# User Interface Class for the EVM
class EVM_UI:
    def __init__(self):
        self.evm = EVM()
        self.run()

    def display_menu(self):
        """Display the menu for the user."""
        print("\nElectronic Voting Machine")
        print("1. Add Candidate")
        print("2. Add Voter")
        print("3. List Candidates")
        print("4. List Voters")
        print("5. Cast Vote")
        print("6. Show Results")
        print("7. Generate Report")
        print("8. Exit")

    def get_choice(self):
        """Get user's choice."""
        while True:
            try:
                choice = int(input("Enter your choice (1-8): "))
                if 1 <= choice <= 8:
                    return choice
                else:
                    print("Invalid choice. Please choose a number between 1 and 8.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def handle_choice(self, choice):
        """Handle user's menu choice."""
        if choice == 1:  # Add Candidate
            name = input("Enter candidate name: ")
            party_name = input("Enter party name: ")
            self.evm.add_candidate(name, party_name)
        
        elif choice == 2:  # Add Voter
            name = input("Enter voter name: ")
            age = int(input("Enter voter age: "))
            self.evm.add_voter(name, age)

        elif choice == 3:  # List Candidates
            self.evm.list_candidates()

        elif choice == 4:  # List Voters
            self.evm.list_voters()

        elif choice == 5:  # Cast Vote
            voter_id = int(input("Enter voter ID: "))
            candidate_id = int(input("Enter candidate ID to vote for: "))
            self.evm.vote(voter_id, candidate_id)

        elif choice == 6:  # Show Results
            self.evm.show_results()

        elif choice == 7:  # Generate Report
            self.evm.generate_report()

        elif choice == 8:  # Exit
            self.evm.save_data()
            print("Exiting the system. All data has been saved.")
            exit()

    def run(self):
        """Run the main loop of the EVM system."""
        while True:
            self.display_menu()
            choice = self.get_choice()
            self.handle_choice(choice)


if __name__ == "__main__":
    EVM_UI()
