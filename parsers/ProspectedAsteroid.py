def parse(entry):
    return entry


CONTEXT = """
A prospector returned info about an asteroid.
Notify if the asteroid has a core first (MotherlodeMaterial) then composition (MotherlodeMaterial_Localised) and density (Content_Localised).
Sort other materials in market value order. Dont mention the proportions.
"""

## { "timestamp":"2025-03-03T02:36:22Z", "event":"ProspectedAsteroid", "Materials":[ { "Name":"Bromellite", "Proportion":12.805447 }, { "Name":"MethaneClathrate", "Name_Localised":"Methane Clathrate", "Proportion":7.995997 } ], "MotherlodeMaterial":"LowTemperatureDiamond", "MotherlodeMaterial_Localised":"Low Temp. Diamonds", "Content":"$AsteroidMaterialContent_Medium;", "Content_Localised":"Material Content: Medium", "Remaining":100.000000 }
