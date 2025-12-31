
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
        # Dn ——> Mn/On
        for index, row in plot_dialogue.iterrows():
            return [row['dialogue_id'], row['dialogue_type'], row['next_dialogue_id']]

    def message(self, dialogue_id):
        # Mn[order].value == [n:n]
        for index2, row2 in plot_dialogue_message.iterrows():
            if row2['dialogue_id'] == dialogue_id:
                print(f"{row2['order']}. {row2['user_name']}: {row2['text']}")

    def option(self):
        pass

    def run(self):

        text = ""
        dialogue_id = ""
        next_dialogue_id = ""
        

        # Pn
        print("Plot_xxx")

        # P ——> Dn
        # Dn ——> Mn/On

        # dialogue_id = plot_dialogue['dialogue_id'].values
        # _dialogue = len(dialogue_id) - 1
        # dialogue_type = plot_dialogue['dialogue_type'].values
        # next_dialogue_id = plot_dialogue['next_dialogue_id'].values

        # for i in range(_dialogue):
        #     # print(dialogue_id[i], next_dialogue_id[i], dialogue_type[i])
        #     print(f"次数{i}: {dialogue_id[i]}, {dialogue_type[i]}, {next_dialogue_id[i]}")

        #     # Dn[dialogue_type] == end ——> P
        #     if dialogue_type[i] == 'end':
        #         print("游戏结束")
        #         break

        #     # Dn ——> Mn ——> text
        #     if dialogue_type[i] == 'normal':

        #         print(f"Dialogue_id: {dialogue_id[i]}, Next_dialogue_id: {next_dialogue_id[i]}")
                
        #         message_id = plot_dialogue_message['message_id'].values
        #         _dialogue_id = plot_dialogue_message['dialogue_id'].values
        #         _message = len(_dialogue_id)
        #         print(_message)
        #         order = plot_dialogue_message['order'].values
        #         user_name = plot_dialogue_message['user_name'].values
        #         text = plot_dialogue_message['text'].values

        #         # Mn[order].value == [n:n]
        #         for _i in range(_message): # i和_i需要区分开来
        #             # print(message_id[_i], _dialogue_id[_i], next_dialogue_id[i], order[_i], user_name[_i], text[_i])

        #             if _dialogue_id[_i] == next_dialogue_id[i]:
        #                 print(f"{message_id[_i]}_{order[_i]}. {user_name[_i]}: {text[_i]}")
        #             else:
        #                 continue
            
        #     # Dn(type=option) ——> On ——> next Dn
        #     elif dialogue_type[i] == 'option':

        #         order = plot_dialogue_option['order'].values
        #         _option = len(order)
        #         option_text = plot_dialogue_option['option_text'].values
        #         next_dialogue_id = plot_dialogue_option['next_dialogue_id'].values

        #         # On[order].value == [n:n]
        #         for _i in range(_option):
        #             print(f"{order[_i]}：{option_text[_i]}")
                

        #         player_choice = int(input("请输入选项编号：")) - 1 
                

        #         print(f"你选择了：{option_text[order[player_choice] - 1]}")
        #         print(next_dialogue_id[order[player_choice] - 1])
        #         next_dialogue_id = plot_dialogue[plot_dialogue['dialogue_id'] == next_dialogue_id[order[player_choice] - 1]]['next_dialogue_id']
        #         print(f"下一个对话ID: {next_dialogue_id}")


        print("===============================================================================")

        current_dialogue_id = plot_dialogue['start_dialogue_id'].values[0]
        print(current_dialogue_id)
        current_history = []
        # yield # yield是生成器函数                      

        for index, row in plot_dialogue.iterrows():
            cud_id = current_dialogue_id
            dia_id = row['dialogue_id']
            dia_type = row['dialogue_type']
            nedia_id = row['next_dialogue_id']

            print(f"次数{index}: {dia_id}, {cud_id}, {dia_type}, {nedia_id}")

            # Dn[dialogue_type] == end ——> P
            if dia_type == 'end':
                related_end = None
                for index, row in plot_dialogue_end.iterrows():
                # 如果是字符串，尝试解析为列表
                    history_list = eval(row['currect_history'])  # 注意：eval有安全风险
                    if history_list == current_history:
                        related_end = row
                        break

                    elif row['currect_history'] == current_history:
                        related_end = row
                        break

                if related_end is not None:
                    print(f"结局：{related_end['text']}")
                    break
                else:
                    print("未找到匹配的结局")

            # Dn ——> Mn ——> text
            if dia_type == 'normal' and dia_id == cud_id:                
                # Mn[order].value == [n:n]
                related_messages = plot_dialogue_message[plot_dialogue_message['dialogue_id'] == nedia_id]
                # print(related_messages)

                for _, msg_row in related_messages.iterrows():
                    print(f"{msg_row['message_id']}_{msg_row['order']}. {msg_row['user_name']}: {msg_row['text']}")

                current_history.append(dia_id)



            # Dn(type=option) ——> On ——> next Dn
            elif dia_type == 'option':
                # On[order].value == [n:n]
                # print(plot_dialogue['dialogue_id'] == dialogue_id)
                related_options = plot_dialogue_option[plot_dialogue_option['dialogue_id'] == nedia_id]
                # print(related_options)

                # print(related_options['order'].values, related_options['option_text'].values)

                for _, opt_row in related_options.iterrows():
                    print(f"{opt_row['order']}：{opt_row['option_text']}")

                player_choice = input("请选择：")

                # opt_row = related_options['order'].values[player_choice]
                # opt_text = related_options['option_text'].values[player_choice]

                while True:

                    selected_options = related_options[related_options['order'] == int(player_choice)]
                    print(selected_options)

                    if not selected_options.empty:
                        selected_option = selected_options.iloc[0]
                        print(f"你选择了：{selected_option['option_text']}")

                        # print(opt_row['next_dialogue_id'])
                        cud_id = current_dialogue_id = selected_option['next_dialogue_id']

                        print(f"下一个对话ID: {cud_id}")

                        current_history.append(dia_id)
                        break
                    else:
                        print("无效的选择, 请重新选择。")
                        player_choice = input("请选择：")
        
            

        print(f"历史记录：{current_history}")
            

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
