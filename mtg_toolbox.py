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

class Card_Type:
    
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
        