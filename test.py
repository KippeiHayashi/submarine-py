import json

json_ = json.dumps({
                "result": {
                    "attacked": {
                        "position": [2,3],
                        "hit": "s"
                    }
                },
                "condition": {
                    "me": {
                        "w": {
                            "hp": 2,
                            "position": [0, 0]
                        },
                        "c": {
                            "hp": 2,
                            "position": [0, 4]
                        },
                        "s": {
                            "hp": 1,
                            "position": [1, 0]
                        }
                    }
                }
            })


cond = json.loads(json_)['result']['attacked']


default_list = [[False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False]]



enemy_firld = {
            "w" : default_list,
            "c" : default_list,
            "s" : default_list
        }






def write_possible_field(field, position):
    (x,y) = (position[1],position[0])
    for i in range(-1,2):
        for j in range(-1,2):
            if (0 <= x + i  <= 4) and (0 <= y + j  <= 4):
                field[x + i][y + j] = True


def move_field(field, distance):
    (r,c) = (distance[1], distance[0])
    if c == 0 and r > 0:
        print("これ")
        for i in range(len(field)):
            for j in range(len(field)):
                if field[i][j]:
                    field[i][j] = False
                    if (0 <= r + i  <= 4) and (0 <= c + j <= 4):
                        field[i + r][j + c] = True

    elif c == 0 and r < 0:
        for i in range(len(field)-1, -1, -1):
            for j in range(len(field)):
                if field[i][j]:
                    field[i][j] = False
                    if (0 <= r + i  <= 4) and (0 <= c + j <= 4):
                        field[i + r][j + c] = True


    elif r == 0 and c > 0:
        for i in range(len(field)):
            for j in range(len(field)):
                if field[j][i]:
                    field[j][i] = False
                    if (0 <= j + r <= 4) and (0 <= i + c <= 4):
                        field[j + r][i + c] = True

    else:
        for i in range(len(field)-1, -1, -1):
            for j in range(len(field)):
                if field[j][i]:
                    field[j][i] = False
                    if (0 <= j + r <= 4) and (0 <= i + c <= 4):
                        field[j + r][i + c]  = True



list =          [[False, False, True, False, False],
                [False, True, False, False, False],
                [False, False, True, False, False],
                [False, True, False, False, False],
                [False, False, False, False, False]]

print(list)
move_field(list, [1,0])
print(list)