import time

class CountdownTimer:
    def __init__(self, duration):
        # Initialize with the countdown duration in seconds
        self.duration = duration
        self.remaining_time = duration

    def start(self):
        """Start the countdown timer"""
        print(f"Starting countdown: {self.duration} seconds")
        
        # Countdown loop
        while self.remaining_time > 0:
            mins, secs = divmod(self.remaining_time, 60)
            time_format = f"{mins:02d}:{secs:02d}"
            print(time_format, end="\r")
            time.sleep(1)
            self.remaining_time -= 1
        
        # Time is up
        print("00:00")
        print("Time's up!")
    
    def reset(self):
        """Reset the timer to the original duration"""
        self.remaining_time = self.duration
        print(f"Timer reset to {self.duration} seconds.")

    def pause(self):
        """Pause the countdown timer"""
        print("Timer paused.")
        return self.remaining_time

    def resume(self, remaining_time):
        """Resume the countdown from where it left off"""
        self.remaining_time = remaining_time
        self.start()

# Main interface for the countdown timer
def main():
    while True:
        print("\nCountdown Timer")
        print("1. Start Timer")
        print("2. Pause Timer")
        print("3. Reset Timer")
        print("4. Exit")
        
        option = input("Choose an option: ")

        if option == "1":
            try:
                seconds = int(input("Enter countdown time in seconds: "))
                timer = CountdownTimer(seconds)
                timer.start()
            except ValueError:
                print("Please enter a valid number.")

        elif option == "2":
            remaining_time = timer.pause()

        elif option == "3":
            timer.reset()

        elif option == "4":
            print("Exiting the countdown timer...")
            break

        else:
            print("Invalid option. Please choose again.")

if __name__ == "__main__":
    main()
