from change_idp_file import readCode
import re

ordering = ['Low','Medium','High']
# input = 'priority.txt'

def getOrdering(input):
    lines = readCode(input)
    relevance_dict = {}
    i=1
    types = []
    for line in lines :
        match = re.match(r'\w+',line)
        if match:
            # print(line)
            types.append(line.strip('\n\t '))     
        else:
            # print(ordering)
            relevance_dict[ordering[-i]] = types
            types = []
            i+=1
        if line == lines[-1] and re.match(r'\w+',line):
            relevance_dict[ordering[-i]] = types
    # print(relevance_dict)
    # print(relevance_dict['Low'])
    return relevance_dict

def convertName(types,relevant):
    # print(types)
    for i in range(len(types)):
        for j in range(len(relevant)):
            if types[i] in relevant[j]:
                types[i] = relevant[j]
    # print(types)
    return types
# !s1,s2 in Security: distance(s1,s2) = (if f_SecurityTypes_4_f (s1)~= f_SecurityTypes_4_f (s2) then 20 else 0).
def distTheory(relevance_dict:dict,goal:str,relevant:str):
    a = f'{goal}__0'
    b = f'{goal}__1'
    dist_theory = f'!{a},{b} in {goal}: distance({a},{b}) = '
    dist_theory_list = []
    for i in range(len(ordering)):
        types = relevance_dict[ordering[i]] 
        types = convertName(types,relevant)
        # print(types)
        if i == 0:
            order_score = 1
        else:
            order_score += len(relevance_dict[ordering[i-1]])*order_score
        for typ in types:
            dist_theory_list.append(f'(if {typ}({a}) ~= {typ}({b}) then {order_score} else 0)')
    
    dist_theory += ' + '.join(dist_theory_list) + '.'
    # print(dist_theory)
    return dist_theory
