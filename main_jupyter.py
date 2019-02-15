def main():
    import pandas as pd
    from googletrans import Translator
    import nltk
    import re
    from IPython.display import display, HTML
    pd.set_option('display.max_columns', 7)
    pd.set_option('display.max_rows', 1000)
    pd.options.display.max_colwidth = 1000
    pd.options.mode.chained_assignment = None

    def re_pattern_finder(pattern, in_str, result_list):
        result = re.findall(pattern, in_str)
        # clear_wo_patterns = re.sub(pattern, "", in_str)
        if len(result) > 0:
            result_list += result
        # return clear_wo_patterns

    def capacity_detect(tokens):
        # print(tokens)
        capacity_element_list = list()
        capacity_index_list = list()
        tok_str = ' '.join(tokens)
        gram_mll_patt = re.compile(r"\d+\sg\b|\d+\sgr\b|\d+\sml\b|\d+g\b|\d+gr\b|\d+ml\b")
        # number_x_patt = re.compile(r"\d+x")

        re_pattern_finder(gram_mll_patt, tok_str, capacity_element_list)
        for element in capacity_element_list:
            part_element = element.split(' ')
            # print('part element', part_element)
            # print(len(part_element))
            if len(part_element) == 1:
                capacity_index_list.append(tokens.index(part_element[0]))
            elif len(part_element) > 1:
                buff_index = list()
                for part in part_element:
                    buff_index.append(tokens.index(part))
                buff_index.sort(key=int)
                # print(buff_index)
                for el in range(len(buff_index) - 1):
                    if buff_index[el + 1] - buff_index[el] == 1:
                        capacity_index_list.append(buff_index[el])
        return capacity_index_list
        # print(tok_str)
        # print(capacity_index_list)
        # print(capacity_element_list)
        # tok_str = re_pattern_finder(number_x_patt, tok_str, capacity_index_list)

    def quantity_detect(tokens, ignore_index):  # , str_wo_capacity
        quantity_index_list = list()
        quantity_element_list = list()
        tok_str = ' '.join(tokens)

        number_x_patt = re.compile(r"\d+\b|\d+\sx\b|\d+x\b")

        re_pattern_finder(number_x_patt, tok_str, quantity_element_list)

        for element in quantity_element_list:
            part_element = element.split(' ')
            # print('part element', part_element)
            # print(len(part_element))
            if len(part_element) == 1:
                part_index = tokens.index(part_element[0])
                if part_index not in ignore_index:
                    quantity_index_list.append(part_index)
            elif len(part_element) > 1:
                buff_index = list()
                for part in part_element:
                    buff_index.append(tokens.index(part))
                buff_index.sort(key=int)
                # print(buff_index)
                for el in range(len(buff_index) - 1):
                    if buff_index[el + 1] - buff_index[el] == 1:
                        if buff_index[el] not in ignore_index:
                            quantity_index_list.append(buff_index[el])
        return list(set(quantity_index_list))

    def tare_detect(tokens, tare_dict):
        tare_entity = dict()
        for token in tokens:
            if token in tare_dict:
                tare_entity[tokens.index(token)] = tare_dict[token]
        return tare_entity

    def food_entity_detect(tokens, food_list):
        food_entity_index = list()
        for token in tokens:
            try:
                food_list.index(token)
            except ValueError:
                pass
            else:
                # print(token)
                food_entity_index.append(tokens.index(token))
        return food_entity_index

    def same_index_checker(entity_index, range):
        for item in entity_index:
            if item in range:
                return item
        return None

    def result_entity(food_index, capacity_index, quantity_index, tare_dict, tokens):
        result_return = str()
        tare_index = list(tare_dict.keys())

        for food in food_index:
            if food_index.index(food) == 0:
                food_range = range(0, food + 1)
            else:
                food_range = range(food_index[(food_index.index(food) - 1)], food + 1)

            quantity_cheker = same_index_checker(quantity_index, food_range)
            capacity_cheker = same_index_checker(capacity_index, food_range)
            tare_cheker = same_index_checker(tare_index, food_range)

            if quantity_cheker is None and \
                    tare_cheker is None and \
                    capacity_cheker is not None:
                result_item = str(re.findall(r'\d+', tokens[capacity_cheker])[0])
                result = str(result_item + " gramme of " + str(tokens[food]) + '\n')
                result_return += result
            elif quantity_cheker is None and \
                    tare_cheker is not None and \
                    capacity_cheker is None:
                result_item = tare_food_dict[tokens[tare_cheker]]
                result = str(str(result_item) + " gramme of " + str(tokens[food]) + '\n')
                result_return += result
            elif quantity_cheker is not None and \
                    tare_cheker is None and \
                    capacity_cheker is None:
                result_item = str(re.findall(r'\d+', tokens[quantity_cheker])[0])
                result = str(result_item + " units of " + str(tokens[food]) + '\n')
                result_return += result
            elif quantity_cheker is not None and \
                    tare_cheker is not None and \
                    capacity_cheker is None:
                qua_item = int(tokens[quantity_cheker])
                tare_item = int(tare_food_dict[tokens[tare_cheker]])
                result_item = qua_item * tare_item
                result = str(str(result_item) + " gramme of " + str(tokens[food]) + '\n')
                result_return += result
            '''elif quantity_cheker is None and \
                    tare_cheker is None and \
                    capacity_cheker is None:
                result = str("1 units of " + str(tokens[food]))
                print(result)'''
        return result_return

    food_list = list()
    with open('food.csv') as csvfile:
        for row in csvfile:
            line = csvfile.readline()
            item = line.split(',')
            food_list.append(item[0][1:].lower())  # [1:] очистка от кавычек

    g_food_list = list()
    with open('generic-food.csv') as csvfile2:
        for row in csvfile2:
            line = csvfile2.readline()
            item = line.split(',')
            # print(item)
            g_food_list.append(item[0].lower())

    v_f_food_list = list()
    with open('v_f_food.csv') as csvfile3:
        for row in csvfile3:
            v_f_food_list.append(str(row)[:-1].lower())

    all_food_list = food_list + g_food_list + v_f_food_list
    # print(all_food_list)

    tare_food_dict = dict()
    columns = ['tare', 'capacity']
    data = pd.read_csv('food_tare.csv', delimiter=',', names=columns)
    for index, row in data.iterrows():
        tare_food_dict[row.tare] = row.capacity

    translator = Translator()

    columns = ['Raw_text', 'english', 'coma_separate', 'food_entity']
    data = pd.read_csv('food_test.csv', delimiter='\n', names=columns)

    for index, row in data.iterrows():
        row_food = str()
        english_str = translator.translate(row.Raw_text, dest='en').text
        data['english'][index] = english_str
        data['coma_separate'][index] = english_str.split(',')
        for coma_lines in data.coma_separate[index]:
            line_tokens = nltk.word_tokenize(coma_lines)

            food_list = food_entity_detect(line_tokens, all_food_list)
            capacity_list = capacity_detect(line_tokens)
            quantity_list = quantity_detect(line_tokens, capacity_list)
            tare_dict = tare_detect(line_tokens, tare_food_dict)

            line_result = result_entity(food_list,
                                        capacity_list,
                                        quantity_list,
                                        tare_dict,
                                        line_tokens)
            row_food += line_result
        data['food_entity'][index] = row_food
    data.drop(['coma_separate'], axis=1, inplace=True)
    display(HTML(data.to_html().replace("\\n", "<br>")))
