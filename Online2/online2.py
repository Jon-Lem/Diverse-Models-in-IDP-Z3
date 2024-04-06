# Programma dat zoekt naar n oplossingen die een totale afstand hebben van k
# Dus k is de som van d(sx,sy) voor sx,sy deel van de oplossingen verzameling

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
    # relation = " Index * Index -> Bool"
    # goal = "queen"
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
    # print(dist_theory)
    # print(element)
    return dist_theory

    

def insertSol(lines:list,n:int,k:int,goal:str):

    type_sol = "type solution := {"
    for i in range(1,n):
        type_sol += f"s{i},"
    type_sol+=f"s{n}" + "}"
    k_voc = "k: () -> Int"
    k_struc = f"k := {k}."
    dist_voc = "distance: solution * solution -> Int"
    k_dist_theory = " sum{{distance(solution__x,solution__y) | solution__x,solution__y in solution: solution__x ~= solution__y }}/2 > k()."
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
    

    lines.insert(index,type_sol + end)
    lines.insert(index+2,k_voc + end)
    lines.insert(index+2,dist_voc +end )


    target="structure"
    index = indexsearch(lines,target)
    lines.insert(index+1,k_struc + end)

    target="theory"
    index = indexsearch(lines,target)
    # Update existing theory with solution type
    goal_theory_idx = [i for i in range(len(lines)) if goal in lines[i]]
    # print(goal_theory_idx)
    pattern = r'\b' + re.escape(goal) + r'\s*\((.*?)\)'
    for i in goal_theory_idx:
        if i < index:
            continue
        lines[i] = re.sub(pattern, re.escape(goal) + r'(solution__0, \1)', lines[i])
        lines[i] = "!solution__0 in solution:" + lines[i]
        # print(lines[i])
    # Add parts to theory
    lines.insert(index+1,k_dist_theory + end)
    lines.insert(index+1,dist_theory + end)
    # printCode(lines)

    return 

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('input',type=str,help="Input IDP file")
    parser.add_argument('n',type=int,help="number of solutions")
    parser.add_argument('k',type=int,help="total distance k")
    parser.add_argument('goal',type=str,help="target of the diversity")
    args = parser.parse_args()

    input = args.input # input = "<naam>.idp"
    n = args.n # n=5
    k = args.k  # k=186
    goal = args.goal # goal = "ColourOf"

    for i in range(1,n+1):
        if i == 1:
            k=0
        elif i == 2:
            k=args.k/n
        else:
            k=i*args.k//n

        
        lines = readCode(input)
        insertSol(lines,i,k,goal)
        printCode(lines)
        output = runCode(lines)
        print(output)
        exit()

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
