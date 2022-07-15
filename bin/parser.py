#!/usr/bin/env python3

import pandas as pd
import numpy as np
import argparse

from json import loads
from requests import get

BASE_API_URL = "https://api2.moxfield.com/v2/decks/all/%s"

def parse_URL(URL:str):
    """
    This function takes a moxfield URL as input and output a dictionary
    containing all necessary information
    """

    deck_ID = URL.split("/")[-1]
    target_URL = BASE_API_URL % deck_ID
    deck = loads(get(f"{target_URL}").text)


    return deck

class Card_Type:
    """
    This class parses the types of a card.
    """
    supertypes_list = ["Basic", "Legendary", "Ongoing", "Snow", "World"]
    def __init__(self, type_line):
        self.supertypes = []
        self.card_types = []
        self.subtypes = []
        self.parse_type_line(type_line)

    def parse_type_line(self, type_line) :
        parts = type_line.split('—')
        #type and supertype
        type_and_supertype = parts[0].strip().split(" ")
        for part in type_and_supertype :
            if part in self.supertypes_list :
                self.supertypes.append(part)
            else :
                self.card_types.append(part)
        #subtype
        if len(parts) == 2 :
            subtypes = parts[1].strip().split(" ")
            for subtype in subtypes :
                self.subtypes.append(subtype)

def compute_cmc(mana_cost) :
    """ Return numeric cmc
    :param mana_cost: i.e. "{3}{B}{B}{B}"
    :type mana_cost: String

    :returns: numeric cmc
    :rtype: int
    """
    mana_matrix = {"X":0,"B":1,"R":1,"U":1,"G":1,"W":1}
    manas = mana_cost.replace("}{", "-").replace("{", "").replace("}", "").split("-")
    cmc = 0
    for mana in manas :
        if mana.isnumeric() :
            cmc += int(mana)
        elif mana == "" :
            pass
        else :
            cmc += int(mana_matrix[mana])
    return cmc

def add_card(decklist:dict, cardentry:dict, board:str, id:int):
    """
    This functions adds a card entry to a dictionary
    """
    if len(cardentry["card_faces"]) != 0:
        for face in cardentry["card_faces"]:
            decklist["name"].append(face["name"])
            decklist["cmc"].append(compute_cmc(face["mana_cost"]))
            decklist["text"].append(face["oracle_text"])
            decklist["mana_cost"].append(face["mana_cost"])
            decklist["card_id"].append(id)
            decklist["is_dfc"].append(True)
            decklist["color_identity"].append(cardentry["color_identity"])
            decklist["board"].append(board)


            try:
                decklist["power"].append(face["power"])
                decklist["toughness"].append(face["toughness"])
            except KeyError:
                decklist["power"].append("None")
                decklist["toughness"].append("None")

            decklist["supertype"].append(Card_Type(face["type_line"]).supertypes)
            decklist["type"].append(Card_Type(face["type_line"]).card_types)
            decklist["subtype"].append(Card_Type(face["type_line"]).subtypes)

    else:
        decklist["name"].append(cardentry["name"])
        decklist["cmc"].append(cardentry["cmc"])
        decklist["text"].append(cardentry["oracle_text"])
        decklist["mana_cost"].append(cardentry["mana_cost"])
        decklist["card_id"].append(id)
        decklist["is_dfc"].append(False)
        decklist["color_identity"].append(cardentry["color_identity"])
        decklist["board"].append(board)

        try:
            decklist["power"].append(cardentry["power"])
            decklist["toughness"].append(cardentry["toughness"])
        except KeyError:
            decklist["power"].append("None")
            decklist["toughness"].append("None")

        decklist["supertype"].append(Card_Type(cardentry["type_line"]).supertypes)
        decklist["type"].append(Card_Type(cardentry["type_line"]).card_types)
        decklist["subtype"].append(Card_Type(cardentry["type_line"]).subtypes)


    return decklist

def make_dataset(deck:dict):
    """
    This function takes a dictionary as input and parses it as a pandas
    DataFrame.
    """

    decklist_ = {"name":[],"cmc":[],"text":[],"mana_cost":[],
    "card_id":[], "is_dfc":[], "color_identity" :[], "board":[], "power":[],
    "toughness":[], "supertype":[], "type":[], "subtype":[]}

    id = 0
    for k in deck["companions"].keys():
        decklist_ = add_card(decklist_, deck["companions"][k]["card"],
            board="companion", id=id)
        id += 1

    for k in deck["commanders"].keys():
        decklist_ = add_card(decklist_, deck["commanders"][k]["card"],
            board="commander", id=id)
        id += 1

    for k in deck["mainboard"].keys():
        for _ in range(deck["mainboard"][k]["quantity"]):
            decklist_ = add_card(decklist_, deck["mainboard"][k]["card"], board="mainboard", id=id)
            id += 1

    return pd.DataFrame(decklist_)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DC decklist analysis tool from a moxfield link")
    parser.add_argument("--mox", help="moxfield URL to your decklist", type=str, required=True)
    args = parser.parse_args()

    URL = args.mox
    deck = parse_URL(URL)
    decklist = make_dataset(deck)

    print(decklist.to_csv(index=False))
