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
    return output


def collect(output):
    # Collect solutions
    matches = []
    solutions = []
    pattern = r'distance :='
    s_pattern = r"(s\d+)"
    cpattern = r'ColourOf := (.*)'
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
    colors+=matches[0]
    # print(colors)
    return sol1,colors,solutions

def insertSol(input,sol1,colors,newk):
    #Insert solutions
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        lines = file.readlines()

    # Solutions
    position_to_insert = 4
    oldsol = lines[position_to_insert - 1]
    lines[position_to_insert - 1] = sol1 + '\n'

    # Insert partial solutions
    position_to_insert = 16 
    oldcol = lines[position_to_insert - 1]
    lines[position_to_insert - 1] = colors + '\n'  # Adjust index to 0-based

    # Insert k
    position_to_insert = 25
    oldk = lines[position_to_insert - 1]
    lines[position_to_insert - 1] = newk + '\n'


    BASE = os.path.dirname(os.path.abspath(__file__))
    input ='online2.idp'
    # Open the file in write mode and write the modified lines back to the file
    with open(os.path.join(BASE,input), 'w') as file:
        file.writelines(lines)

    return oldsol,oldcol,oldk



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

    input ='online2.idp'
    output = runIDP(input)
    solutions,colors,sol=collect(output)

    k=100
    aantsol = 3
    dist = len(sol)*k//aantsol
    print(f"distance: {dist}")
    newk = f"k() = {dist}."

    oldsol,oldcol,oldk = insertSol(input,solutions,colors,newk)
    runIDP_(input)
    # oldsol,oldcol,oldk = insertSol(input,oldsol,oldcol,oldk)

main()

