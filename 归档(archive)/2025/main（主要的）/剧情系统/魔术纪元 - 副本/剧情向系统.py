
import pandas as pd
import os

path = os.path.dirname(os.path.abspath(__file__)) # 获取当前文件路径，replace \ to /
print(path)

_plot_dialogue_path = path + "\Dialogue\plot_dialogue_xxx_001.xlsx"
plot_dialogue = pd.read_excel(_plot_dialogue_path) # message_id message text_type user_id user_name
print(_plot_dialogue_path)
print(plot_dialogue)

_plot_path = path + "\Plot\plot_xxx_001.xlsx"
plot = pd.read_excel(_plot_path)
print(_plot_path)
print(plot)

_plot_dialogue_end_path = path + "\Dialogue\End\plot_dialogue_xxx_end_.xlsx"
plot_dialogue_end = pd.read_excel(_plot_dialogue_end_path) # message_id message text_type user_id user_name
print(_plot_dialogue_end_path)
print(plot_dialogue_end)

_plot_dialogue_message_path = path + "\Dialogue\Message\plot_dialogue_xxx_001_message_.xlsx"
plot_dialogue_message = pd.read_excel(_plot_dialogue_message_path) # message_id message text_type user_id user_name
print(_plot_dialogue_message_path)
print(plot_dialogue_message)

_plot_option_path = path + "\Dialogue\Option\option_dialogue_xxx_option_001.xlsx"
plot_dialogue_option = pd.read_excel(_plot_option_path) # message_id message text_type user_id user_name
print(_plot_option_path)
print(plot_dialogue_option)

"""
P ——> Dn
for Dn[dialogue] > [dialogue_type].value > Dn[next_dialogue_id] ——> Mn/On if Dn[dialogue_type] = normal/option?:M,O else: Dn[dialogue_type] == end ——> P
——> Mn[order].value == [n: n]: Mn[message_id] == Dn > Mn[user_name]: Mn[text]
——> Dn[from_dialogue_id] > On[order] > On[option_id].value ——> On[option_text].value == Dn[to_dialogue_id]?: Dn/n

"""


"""
P ——> Dn

for Dn[dialogue] 
  > [dialogue_type].value 
  > Dn[next_dialogue_id] 
  ——> Mn / On

if Dn[dialogue_type] = normal / option ? 
    M, O 
else: 
    Dn[dialogue_type] == end ——> P

——> Mn[order].value == [n:n]
    Mn[message_id] == Dn
    > Mn[user_name] : Mn[text]

——> Dn[from_dialogue_id] 
    > On[order] 
    > On[option_id].value 
    ——> On[option_text].value 
        == Dn[to_dialogue_id] ? 
        : Dn / n


"""


class Player:
    def __init__(self):
        pass

    def plot(self):
        pass

    def dialog(self):
        pass
    #     # Dn ——> Mn/On
    #     for index, row in plot_dialogue.iterrows():
    #         return [row['dialogue_id'], row['dialogue_type'], row['next_dialogue_id']]

    # def message(self, dialogue_id):
    #     # Mn[order].value == [n:n]
    #     for index2, row2 in plot_dialogue_message.iterrows():
    #         if row2['dialogue_id'] == dialogue_id:
    #             print(f"{row2['order']}. {row2['user_name']}: {row2['text']}")

    def option(self):
        pass

    def run(self):

        current_dialogue_id = plot_dialogue['DialogueID'].values[0]
        current_history = []

        while True:
            row = plot_dialogue[plot_dialogue['DialogueID'] == current_dialogue_id].iloc[0]
            dia_type = row['DialogueType']
            default_next_id = row['DefaultNextID']
            messadge_group_id = row['MessageGroupID']

            print(f"\n当前 DIALOGUE: {row['DialogueID']}, 类型: {dia_type}, 下一个DIALOGUE: {default_next_id}, 消息组ID: {messadge_group_id}")

            related = plot_dialogue_message[plot_dialogue_message['MessageGroupID'] == messadge_group_id]

            for _, msg in related.iterrows():
                print(f"{msg['Order']}. {msg['Speaker']}")
                print(f"{msg['Text']}")
                print(f"{msg['Order']}. {msg['Speaker']}：{msg['Text']}")

            # NORMAL
            if dia_type == 'normal':


                current_history.append(current_dialogue_id)
                current_dialogue_id = default_next_id  # 自动转移
                continue

            # OPTION
            elif dia_type == 'option':
                related = plot_dialogue_option[plot_dialogue_option['MessageGroupID'] == messadge_group_id]
                for _, opt in related.iterrows():
                    print(f"{opt['Order']}: {opt['OptionText']}")

                choice = int(input("请选择："))
                selected = related[related['Order'] == choice].iloc[0]
                print(f"你选择了：{selected['OptionText']}")

                current_history.append(current_dialogue_id)
                current_dialogue_id = selected['MessageGroupID']
                continue

            # END
            elif dia_type == 'end':
                print("=== 结局 ===")
                related_end = plot_dialogue_end[plot_dialogue_end['current_history'] == str(current_history)]
                if not related_end.empty:
                    print(related_end.iloc[0]['Text'])
                else:
                    print("无匹配结局")
                print("游戏结束")
                break

            

# ==============================================================================


if __name__ == '__main__':

    game_state = False

    game_Start = input("是否开始游戏？(y/n)：")
    if game_Start == 'y':

        game_state = True

        print("=============================================================================")
        print("开始游戏")
        print("=============================================================================")

        player = Player()
        player.run()

    if game_Start == 'n':
        print("游戏结束")
