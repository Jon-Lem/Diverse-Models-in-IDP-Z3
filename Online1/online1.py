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

def runIDP(lines,goal):
    print("runIDP")
    code = "".join(lines)
    kb = IDP.from_str(code)
    f = io.StringIO()
    with contextlib.redirect_stdout(f):

        kb.execute()

    output = f.getvalue()
    for line in lines:
        # print("hier")
        if line.lstrip().startswith(goal):
            # print(line.rstrip())  # rstrip() removes any trailing newline characters
            range = line.rstrip()
            break
    
    range = re.search(r"\s*([\S]+)$",range).group().lstrip()
    # print(range)
    if(range == "Bool" or range == "Int" or range == "Float" or range == "Real"):
        # print("Predicate")
        pred_or_func = 0
    else:
        # print("Function")
        pred_or_func = 1

    return output, pred_or_func

def insertSol(lines:list,n:int,k:int,goal:str):

    type_sol = "type solution := {"
    for i in range(1,n):
        type_sol += f"s{i},"
    type_sol+=f"s{n}" + "}"
    k_voc = "k: () -> Int"
    k_struc = f"k := {k}."
    dist_func = "distance: solution * solution -> Int"
    dist_theory = " sum{{distance(sx,sy) | sx,sy in solution: sx ~= sy }}/2 > k()."
    end = "\n"

    # Update predicate/function
    target=f"{goal}"
    index = indexsearch(lines,target)
    
    lines[index] = lines[index].split(':')[0] + ": solution *" + lines[index].split(':')[1]
    # print(lines[index])
    lines.insert(index,type_sol + end)
    lines.insert(index+2,k_voc + end)
    lines.insert(index+2,dist_func +end )
    # print(lines[index])
    # print(index)

    target="structure"
    index = indexsearch(lines,target)
    lines.insert(index+1,k_struc + end)

    target="theory"
    lines.insert(index+1,dist_theory + end)
    printCode(lines)

    return 

def runIDP_(lines):

    code = "".join(lines)
    kb = IDP.from_str(code)
    f = io.StringIO()
    with contextlib.redirect_stdout(f):

        kb.execute()
    output = f.getvalue()
    # print(output)

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

    lines = readCode(input)
    print(lines)
    # printCode(lines)
    insertSol(lines,n,k,goal)
    # printCode(lines)
    # output, pred_or_func = runIDP(lines,goal)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
