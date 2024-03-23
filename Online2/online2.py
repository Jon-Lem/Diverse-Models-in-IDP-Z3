from idp_engine import IDP
import contextlib
import io, re, os

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
    # cpattern = r'ColourOf := (.*)'
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

def insertSol(input,sol1,colors,newk,char):
    #Insert solutions
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        lines = file.readlines()

    # Solutions
    position_to_insert = 4
    oldsol = lines[position_to_insert - 1]
    lines[position_to_insert - 1] = sol1 + char 

    # Insert partial solutions
    position_to_insert = 14 
    oldcol = lines[position_to_insert - 1]
    lines[position_to_insert - 1] = colors + char   

    # Insert k
    position_to_insert = 22
    oldk = lines[position_to_insert - 1]
    lines[position_to_insert - 1] = newk + char   

    if(sol1 and colors and newk == None):
        position_to_insert = 22
        oldk = lines[position_to_insert - 1]
        lines[position_to_insert - 1] = newk + char 

    BASE = os.path.dirname(os.path.abspath(__file__))
    input ='online2.idp'
    with open(os.path.join(BASE,input), 'w') as file:
        file.writelines(lines)

    return oldsol,oldcol,oldk

def restoreSol(input,sol1,colors,newk,char):
    #Insert solutions
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        lines = file.readlines()

    # Solutions
    position_to_insert = 4
    lines[position_to_insert - 1] = sol1 + char 

    # Insert partial solutions
    position_to_insert = 14 
    lines[position_to_insert - 1] = colors + char 

    # Insert k
    position_to_insert = 22 
    lines[position_to_insert - 1] = newk + char 

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
    
    n=5
    k=186
    # k=200

    input ='online2.idp'
    predicate = "ColourOf"
    
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


        oldsol,oldcol,oldk = insertSol(input,solutions,colors,newk,char)
        if i == 0:
            oldtext.append(oldsol)
            oldtext.append(oldcol)
            oldtext.append(oldk)
    char = ""
    runIDP_(input)
    if(len(oldtext) == None):
        print("Geen modellen gevonden")
        exit()
    restoreSol(input,oldtext[0],oldtext[1],oldtext[2],char)

if __name__ == "__main__":

    main()
