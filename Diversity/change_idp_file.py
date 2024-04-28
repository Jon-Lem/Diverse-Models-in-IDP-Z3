# Programma dat zoekt naar n oplossingen die een totale afstand hebben van k
# Dus k is de som van d(sx,sy) voor sx,sy deel van de oplossingen verzameling
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics import silhouette_score
from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt
from idp_engine import IDP
import contextlib
import io, re, os
import numpy as np
from typing import Iterator

distcheck = 0

def printCode(lines:list) -> None:
    [print(i) for i in lines]
    return

def indexsearch(lines:list,target:str) -> int:
    for index,line in enumerate(lines):
        if line.strip().startswith(target):
            return index
    return -1

def completeFunc(lines,relevant:list) -> Iterator[str]:
    target = "vocabulary"
    begin_voc = indexsearch(lines,target)
    end_voc = indexsearch(lines[begin_voc:],"}") + begin_voc    
    voc_lines = lines[begin_voc:end_voc]
    # print(voc_lines)
    pattern = r'^\s*(\w+)\s*:\s*\w'
    relevant= [re.match(pattern, line).group(1) for line in voc_lines if re.match(pattern, line)]
    # print(relevant)
    return relevant

def checkFunc(lines:list,relevant:list) -> None:
    target = "vocabulary"
    begin_voc = indexsearch(lines,target)
    end_voc = indexsearch(lines[begin_voc:],"}") + begin_voc
    for i in range(len(relevant)):
        count = 0
        pattern = r'\b' + re.escape(relevant[i]) + r'\b'
        for line in lines[begin_voc:end_voc]:
            if re.search(pattern, line):
                count+=1
        if count == 0:
            print(f"Error: function '{relevant[i]}' could not be found")
            exit()

def readCode(input:str) -> Iterator[str]:
    lines = []
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        # code = file.read()
        lines = file.readlines()
    
    return lines

def runCode(lines):
    code = "".join(lines)
    kb = IDP.from_str(code)
    f = io.StringIO()
    with contextlib.redirect_stdout(f):

        kb.execute()
    output = f.getvalue()
    
    return output

# Haal de belangrijkste 
def dist_expr(relation:str,goal:str) -> str:
    # print(relation)
    relation = relation.split("->")[0].strip()
    # print(relation)    
    relation = relation.split("*")
    relation= [i.strip() for i in relation]
    relation = [(x,relation.count(x)) for x in set(relation)]
    # print(relation)
    dist_theory = ''
    for word,count in relation:
        element = ','.join([f"{word}__{i}" for i in range(count)])
        if count > 1:
            dist_theory += f"#{{{element} in {word}: {goal}(solution__x,{element}) ~= {goal}(solution__y,{element})}}/{count}"
        else:
            dist_theory += f"#{{{element} in {word}: {goal}(solution__x,{element}) ~= {goal}(solution__y,{element})}}"

    return dist_theory

def insertCode(lines:list,n:int,k:int,goal:list,partSol=None,isBool=None,method=None):
    type_sol = "type solution := {"
    for i in range(1,n):
        type_sol += f"s{i},"
    type_sol+=f"s{n}" + "}\n"
    k_theory = f"k() = {k}.\n"

    if(isBool != None and method == "Online2"):
        # Update type solution
        # print(f'============LINES============\n {lines}')
        target="type solution"
        index = indexsearch(lines,target)
        lines[index] = type_sol
        # Update partial solutions
        # Lijst van goals!!!!
        for i in range(len(partSol)):
            target = "structure"
            begin_struct = indexsearch(lines,target)
            end_struct = indexsearch(lines[begin_struct:],"}") + begin_struct
            # print(lines[begin_struct:end_struct])
            # print(goal[i])
            index = indexsearch(lines[begin_struct:end_struct],f'{goal[i]} :=')
            if index != -1:
                index += begin_struct
                tuples_pattern = re.compile(r'\((.*?)\)')
                tuples = tuples_pattern.findall(lines[index])
                # print(tuples)
                formatted_tuples = []
                if lines[index].strip().startswith(f"{goal[i]} := {{(s"):
                    for j in range(1,n+1):
                        formatted_tuples += [f"(s{j},{t.split(',',1)[1]})" for t in tuples]
                    func_struct = ",".join(formatted_tuples)
                    lines[index] = f"{goal[i]} := {{" + func_struct + "}."
                    continue
                else:
                    # for j in range(1,n+1):
                    #     formatted_tuples += [f"(s{j},{t})" for t in tuples]
                    # print(formatted_tuples)
                
                    continue
            # print(f'====partSol====\n {partSol}')
            if(indexsearch(lines,partSol[i][:len(partSol[i])//2]) != -1):
                index = indexsearch(lines,partSol[i][:len(partSol[i])//2])
                lines[index] = partSol[i]
                # print(f'============NEW_LINES============\n {lines}')
            elif(isBool[i]):
                target="theory"
                index = indexsearch(lines,target)+1
                lines.insert(index,partSol[i])
            else:
                target="structure"
                index = indexsearch(lines,target)+1 
                lines.insert(index,partSol[i])
        # Update k
        target = "k() ="
        index = indexsearch(lines,target)
        lines[index] = k_theory

        return

    k_voc = "k: () -> Int\n"
    dist_voc = "distance: solution * solution -> Int"
    k_dist_theory = " sum{{distance(solution__x,solution__y) | solution__x,solution__y in solution: solution__x ~= solution__y }}/2 >= k()."
    end = "\n"

    # Update predicate/function
    dist_theory = "!solution__x,solution__y in solution: distance(solution__x,solution__y) = "   
    cardinal = []
    for func in goal:
        target=f"{func}"
        index = indexsearch(lines,target)
        cardinal.append(dist_expr(lines[index].split(':')[1],func))
        lines[index] = lines[index].split(':')[0] + ": solution *" + lines[index].split(':')[1]
    dist_theory += "+".join(cardinal) + '.'
    # print(dist_theory)
    
    lines.insert(index,type_sol)
    lines.insert(index+2,k_voc)
    lines.insert(index+2,dist_voc +end)

    target="theory"
    index = indexsearch(lines,target)
    end_theory = indexsearch(lines[index:],"}") + index

    for func in goal:
    # Update existing theory with solution type
        # print(func)
        func_theory_idx = [i for i in range(len(lines)) if func in lines[i] and i >= index  and i < end_theory]
        # print(func_theory_idx)
        pattern = r'\b' + re.escape(func) + r'\s*\((.*?)\)'
        for i in func_theory_idx:
            lines[i] = re.sub(pattern, re.escape(func) + r'(solution__0, \1)', lines[i])
            if(func == goal[0]):
                lines[i] = "!solution__0 in solution:" + lines[i]
            index = i

    lines.insert(index+1,k_theory)
    lines.insert(index+1,k_dist_theory + end)
    lines.insert(index+1,dist_theory + end)

    # Update the structure, if relevant functions present
    for func in goal:
        target = "structure"
        begin_struct = indexsearch(lines,target)
        end_struct = indexsearch(lines[begin_struct:],"}") + begin_struct
        index = indexsearch(lines[begin_struct:end_struct],func)
        if index == -1:
            continue
        else: index += begin_struct
        tuples_pattern = re.compile(r'\((.*?)\)')
        tuples = tuples_pattern.findall(lines[index])
        # print(tuples)
        formatted_tuples = []
        for i in range(1,n+1):
            formatted_tuples += [f"(s{i},{t})" for t in tuples]
        # print(formatted_tuples)
        func_struct = ",".join(formatted_tuples)
        lines[index] = f"{func} := {{" + func_struct + "}."

    if(isBool != None and method == "Offline"):
        for i in range(len(isBool)):
            if(isBool[i]):
                target="theory"
                index = indexsearch(lines,target)+1
            else:
                target="structure"
                index = indexsearch(lines,target)+1
            lines.insert(index,partSol[i])

    return 

def checkPredFunc(lines:list,relevant:list) -> Iterator[int]:
    isBool = []
    for rel in relevant: 
        index = indexsearch(lines,rel)
        # print(lines[index])
        range = lines[index].split("->")[1].strip()
        if(range == "Bool"):
            isBool.append(1)
        else:
            isBool.append(0)

    return isBool

def collectSol(output:str,relevant:list,isBool:list): # Neem altijd de eerste oplossing
    partSol = []
    for i in range(len(relevant)):
        # print(f'rel: {relevant[i]}')
        # print('===OUTPUT===')
        # print(output)
        for line in output.split("\n"):
            index = line.find(relevant[i])
            if index != -1:
                break
        # print(f"===LINE===\n {line}")
        # print(f'===INDEX===\n {index}')
        if isBool[i] == 1:
            tuples_pattern = re.compile(r'\((.*?)\)')
            tuples = tuples_pattern.findall(line)
            # print(tuples)
            formatted_tuples = [f"{relevant[i]}({t})" for t in tuples]
            # print(f'formatted_tuples: {formatted_tuples}')
            partsol = " & ".join(formatted_tuples)
            partsol = partsol + "."
            # print(partsol)    
        else:
            # print(relevant[i])
            # print(line)
            partsol = f'{relevant[i]} >> ' + line.split(":=")[1]
        partSol.append(partsol)
    # print(f'partSol:\n {partSol}')
    if partSol[i].strip() == '.':
        print("Error: cannot satisfy given parameters. Change 'n' or 'k' .")
        exit()
    return partSol

def collectBaseSol(lines:list,output:str,relevant:list,isBool:list) -> tuple[int,Iterator[str]]:
    partSol = []
    for i in range(len(relevant)):
        # Als het al in de struct staat moet je niets doen
        target = "structure"
        begin_struct = indexsearch(lines,target)
        end_struct = indexsearch(lines[begin_struct:],"}") + begin_struct
        index = indexsearch(lines[begin_struct:end_struct],relevant[i])
        if index != -1:
            partSol.append("\n")
            continue
        n = 0
        partsol = f'{relevant[i]} >> {{' if isBool[i] == 0 else ''
        for line in output.split('\n'):
            target = "Model"
            if line.strip().startswith(target):
                n+=1
                continue
            target = f"{relevant[i]}"
            if line.strip().startswith(target):      
                if isBool[i] == 1:
                    tuples_pattern = re.compile(r'\((.*?)\)')
                    tuples = tuples_pattern.findall(line)
                    # print(line)
                    # print(tuples)
                    formatted_tuples = [f"{relevant[i]}(s{n}, {t})" for t in tuples]
                    # print(formatted_tuples)
                    part_sol = " & ".join(formatted_tuples)
                    partsol += part_sol + " & "
                    # print(partsol)    
                else:
                    result_pattern = r"(\b\w+(?:,\w+)?)\s*->\s*(\w+)"
                    match = re.findall(result_pattern,line)
                    formatted_tuples = [f"(s{n},{domain}) -> {range}" for domain,range in match]
                    part_sol = ", ".join(formatted_tuples)
                    partsol += part_sol + " , "
        partsol = partsol[:-2]+ '}.' if isBool[i] == 0 else  partsol[:-2]+'.'
        partSol.append(partsol)
    return n,partSol

def simMatrix(output,goal):
    for k in range(len(goal)):
        models = []
        pattern = re.escape(goal[k]) + r' := {(.*)}'
        for line in output.split("\n"):
            match = re.match(pattern,line)
            if match:
                try: # If predicate
                    model = eval("[" + match.group(1) + "]")
                except: # If function
                    model = re.findall( r'->\s*(\w+)', match.group(1))
                    # print(model)
                    # print(len(model))
                    # exit()
                models.append(model)
        # print(models)
        if k==0:
            simMat = [[0 for _ in range(len(models))] for _ in range(len(models))]
        for i in range(len(models)):
            for j in range(len(models)):
                # distance = len(set(models[j]) - set(models[i]))
                distance = sum(x != y for x, y in zip(models[i], models[j]))
                if k==0:
                    simMat[i][j] = distance
                else:
                    simMat[i][j] += distance
                # print(f"simMat[{i}][{j}] = {simMat[i][j]}")
    
    return simMat
def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)

def distCheck(simMat,solutions,k):
    print(solutions)
    sum_distance = 0
    for i in range(len(solutions)):
        for j in range(len(solutions)):
            a = solutions[i]
            b = solutions[j]
            sum_distance += simMat[a][b]
            # print(f'(s{a+1},s{b+1}) -> {simMat[a][b]}')
    if(sum_distance//2 >= k):
        print("distCheck 1")
        print(sum_distance//2)
        global distcheck
        distcheck=1
        return True
    else: 
        print("distCheck 0")
        return False
    
def prettyPrint(simMat,solutions,k):
    dist = []
    for i in range(len(solutions)):
        for j in range(len(solutions)):
            a = solutions[i]
            b = solutions[j]
            dist.append(f'(s{a+1},s{b+1}) -> {simMat[a][b]}')
    distance = ','.join(dist)
    print('distance := {' + distance + '}.')
    print(f'k := {k}.')

def clusterComp(clusters:list,i:int,j:int,l:list):
    if clusters[i] != clusters[j] and l == []:
        return True
    elif clusters[i] != clusters[j] and l != [] :
        for item in l:
            if(clusters[j] == clusters[item]):
                return False
        return True
    else:
        return False

def clustering(simMat,k,n):
    # print(f'distance_threshold = {k//n}')
    linkage_type ='complete'
    best_sil = -1
    best_model = None
    for n_clusters in range(2,len(simMat)):
        clusterer = AgglomerativeClustering(metric='precomputed',n_clusters=n_clusters, linkage=linkage_type)
        model = clusterer.fit(simMat)
        cluster_labels = model.labels_
        silhouette_avg = silhouette_score(simMat, cluster_labels , metric="precomputed", )
        # if (silhouette_avg < 0.17):
        #     break
        # print("For n_clusters =" ,n_clusters, "The average silhouette_score is :", silhouette_avg,)
        if silhouette_avg > best_sil and n_clusters != 2:
            best_sil = silhouette_avg
            best_model = model
            num_cluster = n_clusters
    model = best_model

    # model = AgglomerativeClustering(
    # metric='precomputed',
    # n_clusters=None,
    # distance_threshold = k//n, #Wilt dat elke cluster een afstand van 7 met elkaar heeft
    # linkage=linkage_type
    # ).fit(simMat)

    print(f" Number of clusters: {model.n_clusters_}")
    if(model.n_clusters_ == 1):
        print('Solution is not satisfiable')
        exit()
    # print(set(list(model.labels_)))
    # solutions = [list(model.labels_).index(x) for x in set(list(model.labels_)) ]
    # solutions = solutions[:n]

    # plt.title("Hierarchical Clustering Dendrogram")
    # x = squareform(simMat)
    # temp = linkage(x, linkage_type)
    # dendrogram(temp, above_threshold_color="green", color_threshold=k//n , orientation='right')
    # plt.show()

    # plt.title("Hierarchical Clustering Dendrogram")
    # # plot the top three levels of the dendrogram
    # plot_dendrogram(model, truncate_mode="level", p=3)
    # plt.xlabel("Number of points in node (or index of point if no parenthesis).")
    # plt.show()

    solutions = []
    clusters = list(model.labels_)
    for i in range(len(clusters)):
        l = []
        for j in range(len(clusters)):
            if clusterComp(clusters,i,j,l): 
                if(simMat[i][j] >= k/n):
                    # print(f'(s{i},s{j}) -> {simMat[i][j]}')
                    if i not in solutions: solutions.append(i)
                    if j not in solutions: solutions.append(j)
                    l.append(j)
    n_solutions=solutions[0:n]
    i = 0
    while not distCheck(simMat,n_solutions,k) and len(solutions) > n+i:
        i+=1
        n_solutions = solutions[i:n+i]
    # print(solutions)
    # print(n_solutions)
    solutions = n_solutions
    if(distcheck==0):
        print('Solution is not satisfiable')
        exit()
    prettyPrint(simMat,solutions,k)

    return

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



