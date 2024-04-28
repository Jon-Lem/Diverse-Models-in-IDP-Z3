import re
from change_idp_file import readCode

def ordering(output,goal):
    dictlist = [dict() for _ in range(len(goal))]
    deweylist = []
    for k in range(len(goal)):
        models = []
        dewey = []
        val = 0
        pattern = re.escape(goal[k]) + r' := {(.*)}'
        for line in output.split("\n"):
            match = re.match(pattern,line)
            if match:
                try: # If predicate
                    model = eval("[" + match.group(1) + "]")
                except: # If function
                    model = re.findall( r'->\s*(\w+)', match.group(1))
                models.append(model)
        for i in range(len(models[0])):
            for j in range(len(models)):
                try:
                    dictlist[k][models[j][i]]
                except:
                    dictlist[k][models[j][i]] = val
                    val+=1
            # print(f'dictionary values: {dictlist[k]}')
        num = 0
        for model in models:
            # print(f'Model{num+1}:\n',model)
            num+=1
            dewey.append(translate(model,dictlist[k])) 
        deweylist.append(dewey) #List of lists where each index deweylist corresponds to another function
    # print(f'===Dict===:\n',dictlist)
    # print(len(deweylist[0]))
    print(f'===Deweylist===:\n',deweylist)
    # print(f'===DeweyEncoding===:\n')
    # for i in range(len(goal)):
    #     print(f'{deweylist[i][0]} '),
    return dictlist , deweylist

def diversePriority(dictlist,deweylist):
    diverse_models=[]
    #Take the value of the first model for the first function
    for i in range(len(dictlist)):
        for j in range(deweylist[i]):
            print(f'Dewey:\n {deweylist[i][j]}')
            if j == 0:
                start = deweylist[i][j]
            if(start != deweylist[i][j]):
                diverse_models.append(deweylist[i][j])

    return

def translate(result,valdict):
    dewey=[]
    for i in result:
        dewey.append(valdict[i])
    # print(f'Result:\n {result}')
    # print(f'Dewey Encoding:\n {dewey}')

    return dewey

def priorityOrdering(relevant):
    input = 'priority.txt'
    order = readCode(input)
    order = [i.strip('\n\t ') for i in order if i.strip('\n\t ')]
    # print(order)
    # print(relevant)

    def custom_sort_key(item):
        for name in order:
            if name.lower() in item.lower():
                return order.index(name)
        return len(order)

    relevant = sorted(relevant, key=custom_sort_key)
    # print(relevant)

    return relevant