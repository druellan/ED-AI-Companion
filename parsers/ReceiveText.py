# It is difficult to instruct the AI to ignore information, so, we cleanup the messages we don't care about.
# Other messages, I just want the AI to interpret them, since I can read the text if I want.
# Cruise ship messages can be useful to pirates, but I need to find a way to avoid repetition.

from start import cleanup_event
from components.utils import log


def parse(entry):
    j_message = entry.get("Message")

    # Messages to react on
    interpret_messages = [
        "$Trader_OnEnemyShipDetection",
        "$Miner_OnJumpNoAsteroids",
        "$STATION_docking_denied",
        "$DockingChatter",
        #
        # Police
        "$Police_ArriveInvestigate",
        "$OverwatchCriticalDamage",
        # "$Military_Passthrough",
        #
        # Pirate
        "$Pirate_Arrival",
        "$Pirate_HunterHostileSC",
        "$Pirate_LargeCargoIgnoreThreat",
        "$Pirate_ThreatenTimer",
        "$Pirate_ThreatenSpecific",
        # "$Pirate_OnStartScanCargo",
        "$Pirate_OnDeclarePiracyAttack",
        # "$Pirate_ReminderValue",
        # "$Pirate_ReminderSpecific",
        "$Pirate_StartInterdiction",
        "$BadKarmaCriticalDamage",
        "$Indirect_EnemyReinforcements",
        "$Combat_OnKillReward",
    ]

    if not any(j_message.startswith(msg) for msg in interpret_messages):
        log("event", f"Dropping no relevant message type: {j_message}")
        return False

    return cleanup_event(entry, ["Channel", "From"])


CONTEXT = """
This message has been broadcasted on local space.
Don't read the message content, interpret the message based on "Message" (intention) and "Message_Localised" (content).
Consider the previous message as context and to avoid repetition.
Pay special attention to "$Pirate_ThreatenSpecific" messages.
If you think the message is trivial (no risk, not relevant information provided), ignore the event completely.
"""
# Don't read the message content, just interpret it.
# { "timestamp":"2025-03-03T02:19:22Z", "event":"ReceiveText", "From":"$npc_name_decorate:#name=Pollux;", "From_Localised":"Pollux", "Message":"$Trader_OnEnemyShipDetection03;", "Message_Localised":"Oh no you don't!", "Channel":"npc" }
