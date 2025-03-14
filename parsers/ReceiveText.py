# It is difficult to instruct the AI to ignore information, so, we cleanup the messages we don't care about.
# Other messages, I just want the AI to interpret them, since I can read the text if I want.
# Cruise ship messages can be useful to pirates, but I need to find a way to avoid repetition.

from start import cleanup_event


def parse(entry):
    j_message = entry.get("Message")

    # Only read these messages type
    interpret_messages = [
        "$Trader_OnEnemyShipDetection",
        "$Miner_OnJumpNoAsteroids",
        "$STATION_docking_denied",
        "$DockingChatter",
        # Combat
        "$Police_ArriveInvestigate",
        "$Pirate_HunterHostileSC",
        # "$Pirate_OnStartScanCargo",
        # "$Military_Passthrough",
        "$Pirate_OnDeclarePiracyAttack",
        "$BadKarmaCriticalDamage",
        "$OverwatchCriticalDamage",
        "$Indirect_EnemyReinforcements",
        "$Combat_OnKillReward",
        "$Pirate_Arrival",
    ]

    if not any(j_message.startswith(msg) for msg in interpret_messages):
        print(f"Ignoring the message type {j_message}")
        return False

    return cleanup_event(entry, ["Channel", "From"])


CONTEXT = """
This meesage has been broadcasted on local space.
Interpret the message based on "Message" (intention) and "Message_Localised" (content).
Consider the previous message as context and to avoid repetition.
Don't read the message content, just interpret it.
If you think the message is trivial, ignore it.
"""

# { "timestamp":"2025-03-03T02:19:22Z", "event":"ReceiveText", "From":"$npc_name_decorate:#name=Pollux;", "From_Localised":"Pollux", "Message":"$Trader_OnEnemyShipDetection03;", "Message_Localised":"Oh no you don't!", "Channel":"npc" }
