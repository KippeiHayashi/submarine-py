import sys
import json
import socket
import random
import os, sys
sys.path.append(os.getcwd())
from lib.player_base import Player, PlayerShip

default_field = [[False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False]]



def write_true_field(field, position):
    (x,y) = (position[1],position[0])
    for i in range(-1,2):
        for j in range(-1,2):
            if (0 <= x + i  <= 4) and (0 <= y + j  <= 4):
                field[x + i][y + j] = True
    
def write_false_field(field, position):
    (x,y) = (position[1],position[0])
    for i in range(-1,2):
        for j in range(-1,2):
            if (0 <= x + i  <= 4) and (0 <= y + j  <= 4):
                field[x + i][y + j] = False

def merge_field(field1, field2):
    for i in range(len(field1)):
            for j in range(len(field1)):
                if not field1[i][j] or not field2[i][j]:
                    field2[i][j] = False

def move_field(field, distance):
    (r,c) = (distance[1], distance[0])
    if c == 0 and r > 0:
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
                    if (0 <= r + i  <= 4) and (0 <= c + j <= 4):
                        field[j + r][i + c] = True

    else:
        for i in range(len(field)-1, -1, -1):
            for j in range(len(field)):
                if field[j][i]:
                    field[j][i] = False
                    if (0 <= r + i  <= 4) and (0 <= c + j <= 4):
                        field[j + r][i + c]  = True


def return_true(field):
    true_list = []
    for i in range(len(field)):
            for j in range(len(field)):
                if field[i][j]:
                    true_list.append([i,j])
    return true_list








class MyPlayer(Player):
    def __init__(self):
        # フィールドを5x5の配列として持っている．
        self.field = [[i, j] for i in range(Player.FIELD_SIZE)
                      for j in range(Player.FIELD_SIZE)]
        
        self.enemy_field = {
        # 相手の各船がいる可能性のあるフィールド
            "w" : default_field,
            "c" : default_field,
            "s" : default_field
        }

        # 初期配置を非復元抽出でランダムに決める．
        ps = random.sample(self.field, 3)
        positions = {'w': ps[0], 'c': ps[1], 's': ps[2]}
        super().__init__(positions)

    # 自分の行動のフィードバックから相手の位置を推定
    def update_field_my_turn(self, json_):
        cond = json.loads(json_)['result']['attacked']
        #見つからなかった船のリスト
        not_found_ship = ["w", "c", "s"]
        if "hit" in cond:
            #当たった船をnot_found_shipから削除
            not_found_ship.remove(cond['hit'])
            #当たった船が撃沈した場合、フィールドを全てFalseに
            hp = json.loads(json_)['condition']['enemy'][cond['hit']]
            if hp == 0:
                self.enemy_field[cond['hit']] = default_field
            else:
                #当たった船のフィールドで、その座標の点のみをTrueにする。
                self.enemy_field[cond['hit']] = default_field
                self.enemy_field[cond['hit']][cond['position']] = True

        if "near" in cond:
            for n in range(len(cond['near'])):
                #近くにいた船をnot_found_shipから削除
                not_found_ship.remove(cond['near'][n])
                new_field = default_field
                #座標周り９マスをTrueにする関数write_true_field
                write_true_field(new_field, cond['position'])
                #hitではないので座標の点はFalseにする
                new_field[cond['position'][0]][cond['position'][1]] = False
                #今までの敵船の潜伏可能性フィールドに、今回得た情報を統合
                merge_field(new_field, self.enemy_field[cond['near'][n]])
        
        #見つからなかった船に対しては、座標周り9マスにいなかったからフィールドのその部分をFalseにする
        for i in range(len(not_found_ship)):
            write_false_field(self.enemy_field[not_found_ship[i]], cond['position'])

     # 敵の行動から敵の位置を推定
    def update_field_enemy_turn(self, json_):
        cond = json.loads(json_)['result']
        if "attacked" in cond:
            cond = cond['attacked']
            #attackの情報は、船の種類がわからずその情報を使おうとすると処理が複雑になるので使わない

        else:
            #moveだったら該当船のフィールドを移動させる
            cond = cond['moved']
            move_field(self.enemy_field[cond['ship']], cond['distance'])
            
    def action(self):
        to = []
        w_true_field = return_true(self.enemy_field['w'])
        c_true_field = return_true(self.enemy_field['c'])
        s_true_field = return_true(self.enemy_field['s'])
        #敵船の位置が一つに定まっている場合は、攻撃できるなら攻撃。優先順位はs > c > w
        if len(s_true_field) == 1:
            if self.can_attack(s_true_field[0]):
                to = s_true_field[0]

        elif len(c_true_field) == 1:
            if self.can_attack(c_true_field[0]):
                to = c_true_field[0]
        
        elif len(w_true_field) == 1:
            if self.can_attack(w_true_field[0]):
                to = w_true_field[0]
        
        #上記以外だと相手がいる可能性があり攻撃可能な場所に攻撃　優先順位はs > c > w
                
        elif len(s_true_field) > 1:
            if self.can_attack(s_true_field[0]):
                to = s_true_field[0]

        elif len(c_true_field) > 1:
            if self.can_attack(c_true_field[0]):
                to = c_true_field[0]

        elif len(w_true_field) > 1:
            if self.can_attack(c_true_field[0]):
                to = c_true_field[0]
 

        #どこにも攻撃できなかったらランダムに移動
        if to == []:
            ship = random.choice(list(self.ships.values()))
            to = random.choice(self.field)
            while not ship.can_reach(to) or not self.overlap(to) is None:
                to = random.choice(self.field)
            return json.dumps(self.move(ship.type, to))

        else:
            return json.dumps(self.attack(to))
        

# 仕様に従ってサーバとソケット通信を行う．
def main(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, int(port)))
        with sock.makefile(mode='rw', buffering=1) as sockfile:
            get_msg = sockfile.readline()
            print(get_msg)
            player = MyPlayer()
            sockfile.write(player.initial_condition()+'\n')

            while True:
                info = sockfile.readline().rstrip()
                print(info)
                if info == "your turn":
                    sockfile.write(player.action()+'\n')
                    get_msg = sockfile.readline()
                    player.update_field_my_turn(get_msg)
                    player.update(get_msg)
                elif info == "waiting":
                    get_msg = sockfile.readline()
                    player.update_field_enemy_turn(get_msg)
                    player.update(get_msg)
                elif info == "you win":
                    break
                elif info == "you lose":
                    break
                elif info == "even":
                    break
                else:
                    raise RuntimeError('unknown information')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])