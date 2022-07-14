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