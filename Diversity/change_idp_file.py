# Programma dat zoekt naar n oplossingen die een totale afstand hebben van k
# Dus k is de som van d(sx,sy) voor sx,sy deel van de oplossingen verzameling

from sklearn.cluster import AgglomerativeClustering
from idp_engine import IDP
import contextlib
import io, re, os
import argparse
import time
from typing import Iterator

def printCode(lines):
    [print(i) for i in lines]
    return

def indexsearch(lines:list,target:str) -> int:
    for index,line in enumerate(lines):
        if line.strip().startswith(target):
            return index
    return -1

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
    relation = relation.split("->")[0].strip()
    relation = relation.split("*")
    relation= [i.strip() for i in relation]
    relation = [(x,relation.count(x)) for x in set(relation)]
    # print(relation)
    dist_theory = "!solution__x,solution__y in solution: distance(solution__x,solution__y) = #{"   
    for word,count in relation:
        element = ','.join([f"{word}__{i}" for i in range(count)])
        dist_theory += f"{element} in {word}: {goal}(solution__x,{element}) ~= {goal}(solution__y,{element})" 
    dist_theory += "}/2."

    return dist_theory

def insertCode(lines:list,n:int,k:int,goal:str,partSol=None,isBool=None,method=None):

    type_sol = "type solution := {"
    for i in range(1,n):
        type_sol += f"s{i},"
    type_sol+=f"s{n}" + "}\n"
    k_theory = f"k() = {k}.\n"

    if(isBool != None and method == None):
        # Update type solution
        target="type solution"
        index = indexsearch(lines,target)
        lines[index] = type_sol
        # Update partial solutions
        if(indexsearch(lines,goal[:len(goal)//2]) != -1):
            index = indexsearch(lines,goal[:len(goal)//2])
            lines[index] = goal
        elif(isBool):
            target="theory"
            index = indexsearch(lines,target)+1
            lines.insert(index,goal)
        else:
            target="structure"
            index = indexsearch(lines,target)+1 
            lines.insert(index,goal)
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
    target=f"{goal}"
    index = indexsearch(lines,target)
    if(index == -1):
        print("Error: couldn't be found")
        exit()
    # print(lines[index])
    dist_theory = dist_expr(lines[index].split(':')[1],goal)
    lines[index] = lines[index].split(':')[0] + ": solution *" + lines[index].split(':')[1]
    
    lines.insert(index,type_sol)
    lines.insert(index+2,k_voc)
    lines.insert(index+2,dist_voc +end)
    # printCode(lines)
    target="theory"
    index = indexsearch(lines,target)
    # print(index)
    # Update existing theory with solution type
    goal_theory_idx = [i for i in range(len(lines)) if goal in lines[i] and i > index]
    # print(goal_theory_idx)
    pattern = r'\b' + re.escape(goal) + r'\s*\((.*?)\)'
    for i in goal_theory_idx:
        lines[i] = re.sub(pattern, re.escape(goal) + r'(solution__0, \1)', lines[i])
        lines[i] = "!solution__0 in solution:" + lines[i]
        index = i
        # print(lines[i])
    # Add parts to theory
    lines.insert(index+1,k_theory)
    lines.insert(index+1,k_dist_theory + end)
    lines.insert(index+1,dist_theory + end)
    
    if(isBool != None and method == "Offline"):
        if(isBool):
            target="theory"
            index = indexsearch(lines,target)+1
        else:
            target="structure"
            index = indexsearch(lines,target)+1
        lines.insert(index,partSol)

    return 

def checkPredFunc(lines:list,relevant:str) -> int:

    index = indexsearch(lines,relevant)
    range = lines[index].split("->")[1].strip()
    if(range == "Bool"):
        isBool = 1
    else:
        isBool = 0

    return isBool

def collectSol(output:str,relevant:str,isBool:int): # Neem altijd de eerste oplossing
    for line in output.split("\n"):
        index = line.find(relevant)
        if index != -1:
            break
    # print(index)
    # print(line)

    if isBool == 1:
        tuples_pattern = re.compile(r'\((.*?)\)')
        tuples = tuples_pattern.findall(line)
        # print(tuples)
        formatted_tuples = [f"{relevant}({t})" for t in tuples]
        # print(formatted_tuples)
        partsol = " & ".join(formatted_tuples)
        partsol = partsol + "."
        # print(partsol)    
    else:
        partsol = f'{relevant} >> ' + line.split(":=")[1]

    return partsol

def collectBaseSol(output:str,relevant:str,isBool:int):
    n = 0
    partsol = f'{relevant} >> {{' if isBool == 0 else ''
    for line in output.split('\n'):
        target = "Model"
        if line.strip().startswith(target):
            n+=1
            continue
        target = f"{relevant}"
        if line.strip().startswith(target):      
            if isBool == 1:
                tuples_pattern = re.compile(r'\((.*?)\)')
                tuples = tuples_pattern.findall(line)
                # print(line)
                # print(tuples)
                formatted_tuples = [f"{relevant}(s{n}, {t})" for t in tuples]
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
    partsol = partsol[:-2]+ '}.' if isBool == 0 else  partsol[:-2]+'.'

    return n,partsol

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