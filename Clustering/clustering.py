from idp_engine import IDP
import contextlib
import os, time , io, re


def readCode(input):
    lines = []
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        lines = file.readlines()
    
    return lines

def runIDP(lines):
    print("runIDP")
    code = "".join(lines)
    kb = IDP.from_str(code)
    f = io.StringIO()
    with contextlib.redirect_stdout(f):

        kb.execute()

    output = f.getvalue()
    return output

def simMatrix(output):

    qpos = []
    pattern = r'queen := {(.*)}'
    for line in output.split("\n"):
        match = re.match(pattern,line)
        if match:
            queens = eval("[" + match.group(1) + "]")
            qpos.append(queens)
    print(qpos)


    
    return

def main():
    input = "nqueen.idp"
    foCode = readCode(input)
    output = runIDP(foCode)
    print(output)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))