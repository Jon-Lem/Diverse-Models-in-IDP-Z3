from idp_engine import IDP
import contextlib
import io, os
from typing import Iterator


def printCode(lines:list) -> None:
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