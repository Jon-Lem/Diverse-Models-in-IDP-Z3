from idp_engine import IDP
import contextlib
import io, re, os
import argparse

def printCode(lines):
    [print(i) for i in lines]
    return

def indexsearch(lines,target):
    for index,line in enumerate(lines):
        if line.strip().startswith(target):
            return index
    return -1

def readCode(input):
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


def collect(output,goal,pred_or_func):
    # Collect solutions
    matches = []
    solutions = []
    pattern = r'distance :='
    s_pattern = r"(s\d+)"
    cpattern = re.escape(goal) + r' := (.*)'

    for line in output.split('\n'):
        
        index = line.find(pattern)
        if index != -1: 
            match = re.findall(s_pattern, line)
            if match:            
                match = set(match)
                match = list(match)
                match.sort()
                match.append(f"s{len(match)+1}")
                solutions = match

        matched = re.findall(cpattern, line)
        if matched:
            matches += matched   

    sol1="type solution := {"
    for i in solutions:
        sol1 += f"{i},"
    sol1 = sol1[:-1]
    sol1 +="}"
    # print(sol1)

    # print(matches)  
    if(pred_or_func == 1):
        partsol = f'{goal} >> '
        if(len(matches) < 1):
            return
        partsol+=matches[0] #HIER KAN HET PROGRAMMA CRASHEN
    else:

        tuples_pattern = re.compile(r'\((.*?)\)')
        tuples = tuples_pattern.findall(matches[0])
        # print(tuples)

        formatted_tuples = [f"{goal}({t})" for t in tuples]
        # print(formatted_tuples)
        partsol = " & ".join(formatted_tuples)
        partsol = partsol + "."

    # print(partsol)
    return sol1,partsol,solutions

def insertSol(lines,newk,char,pred_or_func=None,sol1=None,partsol=None,goal=None):

    if(sol1 is None and partsol is None and goal is None ):
        target = "theory"
        index = indexsearch(lines,target) + 2
        lines.insert(index, char)
        lines[index] = newk + char
        return
    
    target = "type solution"
    index = indexsearch(lines,target)
    lines[index] = sol1 + char 

    # The goal is a function
    if(pred_or_func == 1):
        target = f"{goal} >>"
    else:
        target = f"{goal}("
    index = indexsearch(lines,target)
    lines[index] = partsol + char  

    target = "k() ="
    index = indexsearch(lines,target)
    lines[index] = newk + char   
 
    return 


def runIDP_(lines):

    code = "".join(lines)
    kb = IDP.from_str(code)
    f = io.StringIO()
    with contextlib.redirect_stdout(f):

        kb.execute()
    output = f.getvalue()
    print(output)

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
    
    char = "\n"
    oldtext = []
    # pred_or_func = 0
    lines = readCode(input)
    for i in range(n - 2):
        # print("hier")
        if i == 0:
            newk = f" k() = {(k//n)}."
            insertSol(lines,newk=newk,char=char)
            # printCode(lines)
        output, pred_or_func = runIDP(lines,goal)
        if(output == "No models.\n"):
            break
        solutions,partsol,sol=collect(output,goal,pred_or_func)
        dist = len(sol)*k//n
        print(f"distance: {dist}")
        newk = f"k() = {dist}."

        insertSol(lines,newk,char,pred_or_func,solutions,partsol,goal)
        # printCode(lines)

    char = ""
    runIDP_(lines)
    if(len(oldtext) == None):
        print("Geen modellen gevonden")
        exit()

if __name__ == "__main__":

    main()
