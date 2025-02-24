# Still not sure how to tacle this event without repetition. I will keep it simple for now.


def parse(entry):
    if entry["ScanType"] == "NavBeaconDetail":
        notable_planets = [
            "Earth-like body",
            "Water world",
            "Gas giant with water-based life",
            "Gas giant with ammonia-based life",
        ]
        if "PlanetClass" in entry and entry["PlanetClass"] in notable_planets:
            return entry

    return False


CONTEXT = """
We just scanned a body or a nav beacon in the system.
Do a very brief summary.
If the body has some notable caracteristics, notify me.
"""

# { "timestamp":"2025-02-16T01:25:38Z", "event":"Scan", "ScanType":"NavBeaconDetail", "BodyName":"Tian Di C 2", "BodyID":17, "Parents":[ {"Star":4}, {"Null":0} ], "StarSystem":"Tian Di", "SystemAddress":3107710866138, "DistanceFromArrivalLS":24875.620783, "TidalLock":true, "TerraformState":"", "PlanetClass":"High metal content body", "Atmosphere":"", "AtmosphereType":"None", "Volcanism":"", "MassEM":0.000175, "Radius":370685.375000, "SurfaceGravity":0.508208, "SurfaceTemperature":383.426392, "SurfacePressure":0.000000, "Landable":true, "Materials":[ { "Name":"iron", "Percent":21.920944 }, { "Name":"nickel", "Percent":16.580084 }, { "Name":"sulphur", "Percent":15.436411 }, { "Name":"carbon", "Percent":12.980422 }, { "Name":"manganese", "Percent":9.053126 }, { "Name":"phosphorus", "Percent":8.310289 }, { "Name":"zinc", "Percent":5.957293 }, { "Name":"vanadium", "Percent":5.383021 }, { "Name":"cadmium", "Percent":1.702261 }, { "Name":"niobium", "Percent":1.498180 }, { "Name":"tellurium", "Percent":1.177968 } ], "Composition":{ "Ice":0.000000, "Rock":0.667597, "Metal":0.332403 }, "SemiMajorAxis":3069411814.212799, "Eccentricity":0.000027, "OrbitalInclination":0.011102, "Periapsis":171.352210, "OrbitalPeriod":205702.060461, "AscendingNode":164.012212, "MeanAnomaly":355.761029, "RotationPeriod":205768.914150, "AxialTilt":-0.384592, "WasDiscovered":false, "WasMapped":true }
