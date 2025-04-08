import requests

class CurrencyConverter:
    def __init__(self):
        self.api_url = "https://v6.exchangerate-api.com/v6/YOUR_API_KEY/latest/"  # Replace with your API key from ExchangeRate-API
        self.currencies = []  # List to hold supported currencies

    def get_supported_currencies(self):
        """Fetches the list of supported currencies from the API."""
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            if data['result'] == 'success':
                self.currencies = list(data['conversion_rates'].keys())
                return True
        return False

    def get_exchange_rate(self, from_currency, to_currency):
        """Fetches the exchange rate between two currencies."""
        response = requests.get(f"{self.api_url}{from_currency}")
        if response.status_code == 200:
            data = response.json()
            if data['result'] == 'success':
                conversion_rate = data['conversion_rates'].get(to_currency)
                if conversion_rate:
                    return conversion_rate
        return None

    def convert(self, from_currency, to_currency, amount):
        """Converts an amount from one currency to another."""
        rate = self.get_exchange_rate(from_currency, to_currency)
        if rate:
            return amount * rate
        else:
            return None

    def display_supported_currencies(self):
        """Displays the list of supported currencies."""
        print("Supported currencies:")
        for currency in self.currencies:
            print(currency)

    def run(self):
        """Runs the currency converter program."""
        if not self.get_supported_currencies():
            print("Unable to fetch currency data.")
            return

        print("Welcome to the Advanced Currency Converter!")
        print("Fetching supported currencies...")

        while True:
            print("\nSelect the 'from' currency:")
            self.display_supported_currencies()

            from_currency = input("\nEnter the 'from' currency code (e.g., USD, EUR): ").upper()
            if from_currency not in self.currencies:
                print("Invalid 'from' currency code. Please try again.")
                continue

            to_currency = input("\nEnter the 'to' currency code (e.g., USD, EUR): ").upper()
            if to_currency not in self.currencies:
                print("Invalid 'to' currency code. Please try again.")
                continue

            try:
                amount = float(input("\nEnter the amount to convert: "))
                if amount <= 0:
                    print("Please enter a positive amount.")
                    continue
            except ValueError:
                print("Invalid amount. Please enter a valid number.")
                continue

            result = self.convert(from_currency, to_currency, amount)
            if result is None:
                print("Unable to get the conversion rate. Please try again.")
                continue

            print(f"\n{amount} {from_currency} is equal to {result:.2f} {to_currency}.")

            play_again = input("\nWould you like to perform another conversion? (yes/no): ").lower()
            if play_again != "yes":
                print("Thank you for using the Currency Converter. Goodbye!")
                break


if __name__ == "__main__":
    currency_converter = CurrencyConverter()
    currency_converter.run()
