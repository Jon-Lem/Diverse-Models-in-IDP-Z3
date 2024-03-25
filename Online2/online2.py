from idp_engine import IDP
import contextlib
import io, re, os
import argparse

def indexsearch(lines,target):
    for index,line in enumerate(lines):
        if line.strip().startswith(target):
            return index
    return -1


def runIDP(input,goal):
    print("runIDP")
    lines = []
    code=""
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        # code = file.read()
        lines = file.readlines()
    
    for line in lines:
        code += line
    kb = IDP.from_str(code)
    f = io.StringIO()
    with contextlib.redirect_stdout(f):

        kb.execute()

    output = f.getvalue()
    # print(output)

    # print(lines)
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
        # print("wenen")
        # tuples = matches[0].replace(goal + " := {", "").replace("}.", "").split("), ")
        # print(tuples)
        # formatted_tuples = [f"{goal}{t[0]}, {t[1]}, {t[2]})" for t in [tuple(pair.split(", ")) for pair in tuples]]
        # print(formatted_tuples)

        tuples_pattern = re.compile(r'\((.*?)\)')
        tuples = tuples_pattern.findall(matches[0])
        # print(tuples)

        formatted_tuples = [f"{goal}({t})" for t in tuples]
        # print(formatted_tuples)
        partsol = " & ".join(formatted_tuples)
        partsol = partsol + "."

    # print(partsol)
    return sol1,partsol,solutions

def insertSol(input,newk,char,pred_or_func=None,sol1=None,partsol=None,goal=None):
    #Insert solutions
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        lines = file.readlines()

    if(sol1 is None and partsol is None and goal is None ):
        target = "theory"
        index = indexsearch(lines,target) + 2
        lines.insert(index, char)
        lines[index] = newk + char

        BASE = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(BASE,input), 'w') as file:
            file.writelines(lines)

        return


    target = "type solution"
    index = indexsearch(lines,target)
    oldsol = lines[index]
    lines[index] = sol1 + char 

    # The goal is a function
    if(pred_or_func == 1):
        target = f"{goal} >>"
    else:
        target = f"{goal}("
    index = indexsearch(lines,target)
    oldcol = lines[index]
    lines[index] = partsol + char  

    target = "k() ="
    index = indexsearch(lines,target)
    oldk = lines[index]
    lines[index] = newk + char   
 
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'w') as file:
        file.writelines(lines)

    return oldsol,oldcol,oldk

def restoreSol(input,sol1,partsol,newk,pred_or_func,char,goal):
    #Insert solutions
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        lines = file.readlines()

    # Solutions
    target = "type solution"
    index = indexsearch(lines,target)
    oldsol = lines[index]
    lines[index] = sol1 + char

    # Restore partial solutions
    if(pred_or_func == 1):
        target = f"{goal} >>"
    else:
        target = f"{goal}("
    index = indexsearch(lines,target)
    oldcol = lines[index]
    lines[index] = partsol + char  

    # Restore k
    target = "k() ="
    index = indexsearch(lines,target)
    del lines[index]
    # lines[index] = newk + char 

    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'w') as file:
        file.writelines(lines)


def runIDP_(input):
    BASE = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(BASE,input), 'r') as file:

        code = file.read()

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
    for i in range(n - 2):
        # print("hier")
        if i == 0:
            newk = f" k() = {(k//n)}."
            insertSol(input,newk=newk,char=char)
        output, pred_or_func = runIDP(input,goal)
        if(output == "No models.\n"):
            break
        solutions,partsol,sol=collect(output,goal,pred_or_func)
        dist = len(sol)*k//n
        print(f"distance: {dist}")
        newk = f"k() = {dist}."


        oldsol,oldcol,oldk = insertSol(input,newk,char,pred_or_func,solutions,partsol,goal)
        if i == 0:
            oldtext.append(oldsol)
            oldtext.append(oldcol)
            oldtext.append(oldk)
    char = ""
    runIDP_(input)
    if(len(oldtext) == None):
        print("Geen modellen gevonden")
        exit()
    restoreSol(input,oldtext[0],oldtext[1],oldtext[2],pred_or_func,char,goal)

if __name__ == "__main__":

    main()
