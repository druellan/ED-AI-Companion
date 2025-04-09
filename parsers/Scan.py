from start import cleanup_event


def parse(entry):
    clean = cleanup_event(
        entry,
        [
            "Materials",
            "Composition",
            "SemiMajorAxis",
            "Eccentricity",
            "OrbitalInclination",
            "Periapsis",
            "OrbitalPeriod",
            "AscendingNode",
            "MeanAnomaly",
            "RotationPeriod",
            "AxialTilt",
            "SurfacePressure",
            "SurfaceTemperature",
            "SurfaceGravity",
            "MassEM",
            "Radius",
            # "TidalLock",
            # "TerraformState",
            # "PlanetClass",
            # "Atmosphere",
            "AtmosphereType",
            "AtmosphereComposition",
            "Volcanism",
            # "Landable",
            # "WasDiscovered",
            # "WasMapped",
            # "BodyName",
            # "BodyID",
            "Parents",
            "DistanceFromArrivalLS",
        ],
    )

    return clean


# Notable body types  Earth-like body, Water world, Gas giant with water-based life or Gas giant with ammonia-based life

CONTEXT = """
We just scanned a new body or a nav beacon in the system.
On ScanType=NavBeaconDetail, be brief and provide only the most remarkable information.
On ScanType=Detailed, inform about the body characteristics.
"""

# { "timestamp":"2025-04-06T23:23:55Z", "event":"Scan", "ScanType":"Detailed", "BodyName":"HR 7451 7", "BodyID":11, "Parents":[ {"Null":10}, {"Star":0} ], "StarSystem":"HR 7451", "SystemAddress":457137195371, "DistanceFromArrivalLS":816.738617, "TidalLock":false, "TerraformState":"Terraformable", "PlanetClass":"Water world", "Atmosphere":"thin carbon dioxide rich atmosphere", "AtmosphereType":"CarbonDioxideRich", "AtmosphereComposition":[ { "Name":"Oxygen", "Percent":84.519302 }, { "Name":"CarbonDioxide", "Percent":14.637609 }, { "Name":"Water", "Percent":0.558797 } ], "Volcanism":"", "MassEM":0.191448, "Radius":3655856.750000, "SurfaceGravity":5.709294, "SurfaceTemperature":299.815765, "SurfacePressure":6578.182129, "Landable":false, "Composition":{ "Ice":0.000000, "Rock":0.668206, "Metal":0.331794 }, "SemiMajorAxis":230256849.527359, "Eccentricity":0.175361, "OrbitalInclination":7.484907, "Periapsis":227.938658, "OrbitalPeriod":6804993.569851, "AscendingNode":-13.909328, "MeanAnomaly":10.766737, "RotationPeriod":6939100.313914, "AxialTilt":0.344175, "WasDiscovered":false, "WasMapped":true }

# { "timestamp":"2025-02-16T01:25:38Z", "event":"Scan", "ScanType":"NavBeaconDetail", "BodyName":"Tian Di C 2", "BodyID":17, "Parents":[ {"Star":4}, {"Null":0} ], "StarSystem":"Tian Di", "SystemAddress":3107710866138, "DistanceFromArrivalLS":24875.620783, "TidalLock":true, "TerraformState":"", "PlanetClass":"High metal content body", "Atmosphere":"", "AtmosphereType":"None", "Volcanism":"", "MassEM":0.000175, "Radius":370685.375000, "SurfaceGravity":0.508208, "SurfaceTemperature":383.426392, "SurfacePressure":0.000000, "Landable":true, "Materials":[ { "Name":"iron", "Percent":21.920944 }, { "Name":"nickel", "Percent":16.580084 }, { "Name":"sulphur", "Percent":15.436411 }, { "Name":"carbon", "Percent":12.980422 }, { "Name":"manganese", "Percent":9.053126 }, { "Name":"phosphorus", "Percent":8.310289 }, { "Name":"zinc", "Percent":5.957293 }, { "Name":"vanadium", "Percent":5.383021 }, { "Name":"cadmium", "Percent":1.702261 }, { "Name":"niobium", "Percent":1.498180 }, { "Name":"tellurium", "Percent":1.177968 } ], "Composition":{ "Ice":0.000000, "Rock":0.667597, "Metal":0.332403 }, "SemiMajorAxis":3069411814.212799, "Eccentricity":0.000027, "OrbitalInclination":0.011102, "Periapsis":171.352210, "OrbitalPeriod":205702.060461, "AscendingNode":164.012212, "MeanAnomaly":355.761029, "RotationPeriod":205768.914150, "AxialTilt":-0.384592, "WasDiscovered":false, "WasMapped":true }
