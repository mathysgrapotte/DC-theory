#!/usr/bin/env python3

import numpy as np
import pandas as pd
import re
import argparse
import json

from ast import literal_eval

class meta_deck:

    def __init__(self, deck):
        self.deck = deck
        self.id = find_identity(deck)
        self.spells_casting_costs = build_dict(find_identity(deck))


    def fill_costs(self):
        for i in range(len(self.deck)):
            entry = self.deck.iloc[i]

            # Checking if the entry has a mana_cost
            if type(entry["mana_cost"]) is str:
                m = entry["mana_cost"]


                # Processing the mana cost into a list
                m_ = []
                for s in re.findall('\{.*?\}',m):
                    try:
                        temp = int(s[s.find("{")+1:s.find("}")])
                        m_.append(temp)
                    except ValueError:
                        m_.append(s[s.find("{")+1:s.find("}")])

                flag_colorless = True
                for i in self.id:
                    if i in m_:
                        flag_colorless = False
                        count_colorless = 0
                        count_color = 0
                        for cost in m_:
                            if type(cost) is int:
                                count_colorless+=cost
                            else:
                                if i in cost:
                                    count_color+=1
                                else:
                                    count_colorless+=1

                        if count_colorless > 0:
                            key = str(count_colorless) + "C"*count_color
                        else:
                            key = "C"*count_color

                        try:
                            self.spells_casting_costs[i][key].append(entry["name"])
                        except KeyError:
                            self.spells_casting_costs[i][key]=[]
                            self.spells_casting_costs[i][key].append(entry["name"])

                if flag_colorless:
                    key = str(int(entry["cmc"]))
                    try:
                        self.spells_casting_costs["C"][key].append(entry["name"])
                    except KeyError:
                        self.spells_casting_costs["C"][key]=[]
                        self.spells_casting_costs["C"][key].append(entry["name"])

def rapport(list_casting_cost, table):
    mana_source = []
    color_specificity = []
    card_name = []
    n_land_success = []
    on_curve = []

    for i in list_casting_cost.keys():
        if i != 'C':
            for key in list_casting_cost[i].keys():
                if key in table[i].keys():
                    n_land_success_temp = table[i][key]['successRatio']
                    on_curve_temp = table[i][key]['onCurveRatio']*100

                    for n in list_casting_cost[i][key]:
                        color_specificity.append(key)
                        mana_source.append(i)
                        card_name.append(n)
                        n_land_success.append(n_land_success_temp)
                        on_curve.append(on_curve_temp)

    return pd.DataFrame({"mana_source":mana_source, "color_specificity":color_specificity, "card_name":card_name, "n_land_success":n_land_success, "on_curve":on_curve})

def find_identity(deck):
    commanders = deck[deck["board"]=="commander"]
    identity = []
    for i in range(len(commanders)):
        identity += literal_eval(commanders['color_identity'].iloc[i])
    return list(np.unique(identity))

def build_dict(identity):
    dictionary = {}
    for i in identity:
        dictionary[i] = {}
    dictionary["C"] = {}
    return dictionary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DC manabase analysis tool")
    parser.add_argument("--dec", help="path to deck csv as processed by the parser", type=str, required=True)
    parser.add_argument("--karsten", help="path to karsten tables", type=str, required=True)
    args = parser.parse_args()

    deck_path = args.dec
    karsten_path = args.karsten

    deck = pd.read_csv(deck_path)
    class_ = meta_deck(deck)
    class_.fill_costs()
    list_casting_cost = class_.spells_casting_costs

    with open(karsten_path, "r") as f:
        table = json.loads(f.read())

    output = rapport(list_casting_cost, table)

    print(output.to_csv(index=False))
