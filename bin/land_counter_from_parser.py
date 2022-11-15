#!/usr/bin/env python3

from manabase_karsten_analysis import *
import json
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="count number of lands")
    parser.add_argument("--deck", help="deck taken from parser", type=str, required=True)
    args = parser.parse_args()

    deck_path = args.deck
    deck = pd.read_csv(deck_path)
    card_groups = deck.groupby("card_id")
    card_ids, mana = assess_mana_sources(card_groups, find_identity(deck))
    ms,lc = count_mana_sources(mana, find_identity(deck))
    json_result = json.dumps({"land_untapped":ms, "land_count":lc})
    print(json_result)
