#

from start import set_states


def parse(entry):
    fuel_data = {
        "FuelLevel": entry["FuelMain"],
        "FuelReservoir": entry["FuelReservoir"],
    }
    set_states(fuel_data)


CONTEXT = ""

## {'event': 'ReservoirReplenished', 'FuelMain': 27.910135, 'FuelReservoir': 0.52}
