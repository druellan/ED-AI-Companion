# Very hand crafted parser for the Market event.
# Most AIs are able to figure out the market prices and the cargo, but their accuracy decrease the longest the prompt is.
# So, I'm doing most of the important logic by hand, leaving the AI with the tastk of figure out small details and comunicate the information.
# By default we are only going to process the top 3 opportunities to buy and sell.

import json
import os
from config import (
    JOURNAL_DIRECTORY,
)


def parse(entry):
    print("Reading the market file.")
    market_store = os.path.join(JOURNAL_DIRECTORY, "Market.json")

    products_to_report = 3

    try:
        with open(market_store, "r") as file:
            market_content = json.load(file)
    except FileNotFoundError:
        print("Market file not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return []

    cargo_store = os.path.join(JOURNAL_DIRECTORY, "Cargo.json")

    try:
        with open(cargo_store, "r") as file:
            cargo_content = json.load(file)
    except FileNotFoundError:
        print("Cargo file not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return []

    # Filter a bit the cargo content
    # Based on this structure:
    # { "timestamp":"2025-02-15T18:18:09Z", "event":"Cargo", "Vessel":"Ship", "Count":352, "Inventory":[
    # { "Name":"fish", "Count":63, "Stolen":0 },
    # { "Name":"thermalcoolingunits", "Name_Localised":"Thermal Cooling Units", "Count":259, "Stolen":0 },
    # { "Name":"drones", "Name_Localised":"Limpet", "Count":30, "Stolen":0 }
    # ] }

    cargo_content = cargo_content.get("Inventory", [])
    cargo_content = [
        {
            "Name": entry.get("Name"),
            "Count": entry.get("Count", 0),
        }
        for entry in cargo_content
        if entry.get("Name") != "drones" and entry.get("Stolen", 0) == 0
    ]

    # Access the list of items
    items = market_content.get("Items", [])

    buy_goods = [
        {
            "Name_Localised": entry.get("Name_Localised"),
            "Rare": entry.get("Rare"),
            "Stock": entry.get("Stock", 0),
            "Profit": entry.get("MeanPrice", 0) - entry.get("BuyPrice", 0),
        }
        for entry in items
        if entry.get("Producer") is True
    ]

    # Sort the buy_goods based on Profit
    buy_goods.sort(key=lambda x: x.get("Profit", 0), reverse=True)
    buy_goods = buy_goods[:products_to_report]

    rare_goods = [
        {
            "Name_Localised": entry.get("Name_Localised"),
            "Rare": entry.get("Rare"),
            "Profit": entry.get("MeanPrice", 0) - entry.get("BuyPrice", 0),
        }
        for entry in items
        if entry.get("Rare") is True and entry.get("Producer") is True
    ]

    sell_goods = [
        {
            "Name_Localised": entry.get("Name_Localised"),
            "Demand": entry.get("Demand", 0),
            "Profit": entry.get("SellPrice", 0) - entry.get("MeanPrice", 0),
        }
        for entry in items
        if entry.get("Consumer") is True and entry.get("Demand", 0) > 0
    ]

    # Sort the sell_goods based on Profit, reverse order
    sell_goods.sort(
        key=lambda x: (x.get("Profit", 0), x.get("Demand", 0)), reverse=True
    )
    sell_goods = sell_goods[:products_to_report]

    # Build a list of products you can actually sell
    cargo_to_sell = []
    for cargo_item in cargo_content:
        cargo_name = cargo_item.get("Name")
        for market_item in items:
            market_name = (
                market_item.get("Name", "").replace("$", "").replace("_name;", "")
            )
            if market_name == cargo_name:
                cargo_to_sell.append(
                    {
                        "Name_Localised": market_item.get("Name_Localised"),
                        "Demand": market_item.get("Demand", 0),
                        "Profit": market_item.get("SellPrice", 0)
                        - market_item.get("MeanPrice", 0),
                    }
                )

    market_list = {}
    # market_list["cargo_content"] = cargo_content
    market_list["cargo_to_sell"] = cargo_to_sell
    market_list["buy_opportunities"] = buy_goods
    market_list["sell_opportunities"] = sell_goods
    market_list["rare_goods"] = rare_goods
    return market_list


CONTEXT = """
We are about to buy or sell something in the market.
Tell me about opportunities to buy based on profit.
Tell me if I have cargo to sell, let me know if I can make a profit.
Tell me if there are good oportunities to sell.
Tell me if there are rare goods.
"""

## Event Example ##
## { "timestamp":"2025-02-02T14:33:38Z", "event":"Market", "MarketID":128103160, "StationName":"James Sneddon", "StationType":"Orbis", "StarSystem":"Morten-Marte" }
