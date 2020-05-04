import requests
from cachetools import cached
from cachetools import TTLCache


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CurrencyConverter(object, metaclass=Singleton):
    # Get exchange rates
    default = "No Currency"
    api_url = "https://api.exchangeratesapi.io/latest?base=USD"

    def __init__(self):
        pass

    @cached(cache=TTLCache(maxsize=1, ttl=86400))
    def get_rates(self):
        rates = requests.get(self.api_url).json()["rates"]
        rates[self.default] = 1.0
        return rates

    def get_currencies(self):
        rates = [rate for rate in self.get_rates()]
        rates.sort(key=lambda rate: "" if rate == self.default else rate)
        return rates

    def exchange_currency(self, amount, source_currency, dest_currency):
        if (source_currency == dest_currency or source_currency == self.default
                or dest_currency == self.default):
            return amount

        rates = self.get_rates()
        source_rate = rates[source_currency]
        dest_rate = rates[dest_currency]
        new_amount = (float(amount) / source_rate) * dest_rate
        # round to two digits because we are dealing with money
        return round(new_amount, 2)
