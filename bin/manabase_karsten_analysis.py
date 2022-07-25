#!/usr/bin/env python3

import numpy as np
import pandas as pd
import re
import argparse

from ast import literal_eval


#### REGEX PARAMX ####

fetch_regex = r"^{T}, Pay 1 life, Sacrifice .*: Search your library for a.* card, put it onto the battlefield, then shuffle.$"
wubrg_regex = r"Add one mana of any color"
urborg_regex = r"Each land is a Swamp in addition"
slow_fetch_regex = r"Search your library for a basic land card, put it onto the battlefield tapped"
colorless_regex = r"{T}: Add {C}"
pool_regex = r"{T}: Add one mana of any type"
yavimaya_regex = r"Each land is a Forest in addition"

#### FUNCTIONS ####

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

def determine_source(oracle_text, cmd_identity):

    if re.findall(fetch_regex, oracle_text):
        color = cmd_identity
    elif re.findall(wubrg_regex, oracle_text):
        color = cmd_identity
    elif re.findall(slow_fetch_regex, oracle_text):
        color = cmd_identity
    elif re.findall(urborg_regex, oracle_text):
        color = ["B"]
    elif re.findall(yavimaya_regex, oracle_text):
        color = ["G"]
    elif re.findall(colorless_regex, oracle_text):
        color = ["C"]
    elif re.findall(pool_regex, oracle_text):
        color = cmd_identity
    else:
        color = "Undefined"

    return color

def assess_mana_sources(cards, deck_identity):
    card_ids = []
    mana = []
    for i in range(len(cards)):
        temp_identity = []
        group = cards.get_group(i)
        not_land = True
        for i in range(len(group)):
            if "Land" in literal_eval(group.iloc[i]["type"]):
                not_land = False
                c_identity = literal_eval(group.iloc[i]["color_identity"])
                if len(c_identity) > 0:
                    for c in c_identity:
                        temp_identity.append(c)
                else:
                    color = determine_source(group.iloc[i]["text"], deck_identity)
                    if color == "Undefined":
                        temp_identity.append(color)
                    else:
                        for c in color:
                            temp_identity.append(c)


        if not_land:
            temp_identity.append("Not a mana source")
        card_ids.append(group.iloc[0]["card_id"])
        mana.append(''.join(list(np.unique(temp_identity))))
    return card_ids, mana

def count_mana_sources(mana, deck_identity):
    mana_sources = {}
    land_count = 0
    for c in deck_identity:
        mana_sources[c] = 0

    for m in mana:
        if m == 'Undefined':
            land_count+=1
        elif m == "Not a mana source":
            pass
        else:
            land_count+=1
            for c in deck_identity:
                if c in m:
                    mana_sources[c]+=1

    return mana_sources, land_count


def assess_castability(spell_casting_costs, ms, interest_karsten, deck_identity):
    recom = []
    actual = []
    difference = []
    mana_source = []
    castable = []
    name = []
    for c in deck_identity:
        for key in spell_casting_costs[c].keys():
            a_ = ms[c]
            try:
                r_ = interest_karsten[key]
            except KeyError:
                r_ = 1
            dif_ = a_ - r_
            c_ = dif_ >= 0

            for n in spell_casting_costs[c][key]:
                name.append(n)
                actual.append(a_)
                recom.append(r_)
                difference.append(dif_)
                mana_source.append(c)
                castable.append(c_)
    return pd.DataFrame({"card name":name, "interest source":mana_source, "actual nb":actual, "recom nb":recom,
                        "difference":difference, "castable":castable})


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DC Karsten analysis tool")
    parser.add_argument("--dec", help="path to deck csv as processed by the parser", type=str, required=True)
    parser.add_argument("--karsten", help="path to karsten tables", type=str, required=True)
    args = parser.parse_args()

    deck_path = args.dec
    karsten_path = args.karsten

    deck = pd.read_csv(deck_path)
    card_groups = deck.groupby("card_id")

    karsten = pd.read_csv(karsten_path, sep="\t")

    card_ids, mana = assess_mana_sources(card_groups, find_identity(deck))
    ms,lc = count_mana_sources(mana, find_identity(deck))
    meta = meta_deck(deck)
    meta.fill_costs()

    interest_karsten = karsten[karsten["Lands"]==lc].iloc[0]

    castability = assess_castability(meta.spells_casting_costs, ms, interest_karsten, find_identity(deck))

    print(castability.to_csv(index=False))
