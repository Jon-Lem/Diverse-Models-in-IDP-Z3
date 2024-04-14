# Programma dat zoekt naar n oplossingen die een totale afstand hebben van k
# Dus k is de som van d(sx,sy) voor sx,sy deel van de oplossingen verzameling

from sklearn.cluster import AgglomerativeClustering
from idp_engine import IDP
import contextlib
import io, re, os
import argparse
import time
from typing import Iterator

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

    qpos = []
    pattern = re.escape(goal) + r' := {(.*)}'
    for line in output.split("\n"):
        match = re.match(pattern,line)
        if match:
            try:
                queens = eval("[" + match.group(1) + "]")
            # else: queens = "[" + match.group(1) + "]"
            except:
                queens = re.findall( r'->\s*(\w+)', match.group(1))
                # print(queens)
                # print(len(queens))
                # exit()
            qpos.append(queens)
    # print(qpos)

    simMat = [[0 for _ in range(len(qpos))] for _ in range(len(qpos))]
    for i in range(len(qpos)):
        for j in range(len(qpos)):
            # distance = len(set(qpos[j]) - set(qpos[i]))
            distance = sum(x != y for x, y in zip(qpos[i], qpos[j]))
            simMat[i][j] = distance
            # print(f"simMat[{i}][{j}] = {simMat[i][j]}")
    
    return simMat

def clustering(simMat,k):
    model = AgglomerativeClustering(
    metric='precomputed',
    n_clusters=None,
    distance_threshold = k, #Wilt dat elke cluster een afstand van 7 met elkaar heeft
    linkage='complete'
    ).fit(simMat)
    print(model.labels_)
    print(f" Number of clusters: {model.n_clusters_}")
    
    return