from start.py import cleanup_event


def parse(entry):
    entry = cleanup_event(entry, ["SystemAddress"])

    signal_list = {}
    for signal in entry["Signals"]:
        signal_list.append({"Type_Localised": signal["Type_Localised"]})

    entry["Signals"] = signal_list
    return entry


CONTEXT = """
    We detected hotspots for mining.
"""

# {'event': 'SAASignalsFound', 'BodyName': 'Komovoy A 3 A Ring', 'SystemAddress': 11666876147129, 'BodyID': 15, 'Signals': [{'Type': 'LowTemperatureDiamond', 'Type_Localised': 'Low Temp. Diamonds', 'Count': 2}, {'Type': 'Opal', 'Type_Localised': 'Void Opal', 'Count': 1}, {'Type': 'Bromellite', 'Count': 2}], 'Genuses': []}
