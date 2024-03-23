from idp_engine import IDP
import contextlib
import io, re, os
import argparse

def indexsearch(lines,target):
    for index,line in enumerate(lines):
        if line.strip().startswith(target):
            return index
    return -1


def runIDP(input):
    print("runIDP")
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:

        code = file.read()

    kb = IDP.from_str(code)
    f = io.StringIO()
    with contextlib.redirect_stdout(f):

        kb.execute()

    output = f.getvalue()
    print(output)
    return output


def collect(output,predicate):
    # Collect solutions
    matches = []
    solutions = []
    pattern = r'distance :='
    s_pattern = r"(s\d+)"
    cpattern = re.escape(predicate) + r' := (.*)'

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
    colors = 'ColourOf >> '
    if(len(matches) < 1):
        return
    colors+=matches[0] #HIER KAN HET PROGRAMMA CRASHEN
    # print(colors)
    return sol1,colors,solutions

def insertSol(input,sol1,colors,newk,char,predicate):
    #Insert solutions
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        lines = file.readlines()

    target = "type solution"
    index = indexsearch(lines,target)
    oldsol = lines[index]
    lines[index] = sol1 + char 

    target = f"{predicate} >>"
    index = indexsearch(lines,target)
    oldcol = lines[index]
    lines[index] = colors + char  

    target = "k() ="
    index = indexsearch(lines,target)
    oldk = lines[index]
    lines[index] = newk + char   

    if(sol1 and colors and newk == None):
        position_to_insert = 22
        oldk = lines[position_to_insert - 1]
        lines[position_to_insert - 1] = newk + char 

    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'w') as file:
        file.writelines(lines)

    return oldsol,oldcol,oldk

def restoreSol(input,sol1,colors,newk,char,predicate):
    #Insert solutions
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        lines = file.readlines()

    # Solutions
    target = "type solution"
    index = indexsearch(lines,target)
    oldsol = lines[index]
    lines[index] = sol1 + char

    # Insert partial solutions
    target = f"{predicate} >>"
    index = indexsearch(lines,target)
    oldcol = lines[index]
    lines[index] = colors + char  

    # Insert k
    target = "k() ="
    index = indexsearch(lines,target)
    oldk = lines[index]
    lines[index] = newk + char 

    BASE = os.path.dirname(os.path.abspath(__file__))
    input ='online2.idp'
    with open(os.path.join(BASE,input), 'w') as file:
        file.writelines(lines)


def runIDP_(input):
    BASE = os.path.dirname(os.path.abspath(__file__))
    # input ='online2.idp'

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
    parser.add_argument('k',type=int,help="distance k")
    parser.add_argument('predicate',type=str,help="target of the diversity")

    args = parser.parse_args()

    input = args.input # input = "online2.idp"
    n = args.n # n=5
    k = args.k  # k=186
    predicate = args.predicate # predicate = "ColourOf"
    
    char = "\n"
    oldtext = []
    for i in range(n - 2):
        # print("hier")
        output = runIDP(input)
        if(output == "No models.\n"):
            break
        solutions,colors,sol=collect(output,predicate)
        dist = len(sol)*k//n
        print(f"distance: {dist}")
        newk = f"k() = {dist}."


        oldsol,oldcol,oldk = insertSol(input,solutions,colors,newk,char,predicate)
        if i == 0:
            oldtext.append(oldsol)
            oldtext.append(oldcol)
            oldtext.append(oldk)
    char = ""
    runIDP_(input)
    if(len(oldtext) == None):
        print("Geen modellen gevonden")
        exit()
    restoreSol(input,oldtext[0],oldtext[1],oldtext[2],char,predicate)

if __name__ == "__main__":

    main()
