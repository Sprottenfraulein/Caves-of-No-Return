# Generating items left after monster defeat.
import random
from rules import charts


def get_drop(mob_name, lvl):
    treasure_list = charts.treasure
    drop_list = []
    for tr in treasure_list:
        if (tr[2] is None or mob_name in tr[2]) and tr[3] <= lvl:
            drop_list.append(tr)
    return pick_rnd_item(drop_list)

def pick_rnd_item(drop_list):
    if len(drop_list) == 0:
        return None
    chances_sum = 0
    # Calculating sum of all item chances
    for tr in drop_list:
        chances_sum += tr[4]
    roll = random.randrange(1, chances_sum + 1)

    chances_sum = 0
    # Picking item acccording to roll.
    for tr in drop_list:
        chances_sum += tr[4]
        if roll <= chances_sum:
            return tr

def chest(lvl):
    item_list = (
        'ptn_red',
        'ptn_yellow',
        'ptn_blue',
        'sp_unknown',
        # 'key',
        'gold'
    )
    return random.choice(item_list)