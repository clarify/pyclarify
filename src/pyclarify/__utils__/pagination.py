import math

def data_blocks(notbefore, before):
    dt = before - notbefore
    hours = dt.days * 24  + dt.seconds//3600 + 1
    blocks = math.ceil(hours / 960)
    delta = (before - notbefore)/blocks

    date_list = [notbefore]
    for block in range(1, blocks + 1):
        if notbefore + block * delta >= before:
            date_list.append(before)
            break
        else:
            time = notbefore + block * delta
            date_list.append(time)

    return date_list, delta.days

def item_block(num_items):
    item_blocks = int(num_items / 50)
    remainder = num_items % 50
    return item_blocks, remainder
