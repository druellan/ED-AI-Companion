# It is difficult to instruct the AI to ignore information, so, we cleanup the messages we don't care about.
# Other messages, I just want the AI to interpret them, since I can read the text if I want.
# Cruise ship messages can be useful to pirates, but I need to find a way to avoid repetition.


def parse(entry):
    j_message = entry.get("Message")

    # Ignore some messages
    if (
        j_message.startswith("$STATION_")
        or j_message.startswith("$Docking")
        or j_message.startswith("$COMMS_entered")
        or j_message.startswith("$Commuter_AuthorityScan")
        or j_message.startswith("$CruiseLiner_SCPatrol")
        or j_message.startswith("$ConvoyWedding_Patrol")
        # Pirate-specific to ignore
        or j_message.startswith("$Pirate_OnTargetFleeing01")
        or j_message.startswith("$Pirate_LargeCargo")
    ):
        print(f"Ignoring the message type {j_message}")
        return False

    return entry


CONTEXT = """
A meesage has been broadcasted.
Sumarize the content of the message.
On Message "$Trader_OnEnemyShipDetection", notify me that might be some danger in the area.
Be extra brief about messages from pirates.
"""
