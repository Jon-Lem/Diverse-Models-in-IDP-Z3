from idp_engine import IDP
import contextlib
import io, re, os
from typing import Iterator

BASE = os.path.dirname(os.path.abspath(__file__))
input ='../Base/mapcoloring.idp'

def readCode(input:str) -> Iterator[str]:
    lines = []
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE,input), 'r') as file:
        # code = file.read()
        lines = file.readlines()
    
    return lines

with open(os.path.join(BASE,input), 'r') as file:

    code = file.read()


kb = IDP.from_str(code)
f = io.StringIO()
with contextlib.redirect_stdout(f):

    kb.execute()

output = f.getvalue()
# print(output)


models = {}
current_model = None
model_pattern = r'Model (\d+)'
colour_pattern = r"(\w+) -> (\w+)"
solutions = []
relevant = "ColourOf"

for line in output.split('\n'):
    match = re.match(model_pattern, line)
    if match:
        
        current_model = f"s{match.group(1)}"
        solutions.append(current_model)
        if current_model not in models:
            models[current_model] = []
        continue

    if line.strip() == (f'{relevant}'+' := {'):
        # print("hier")
        break

    # Extract country-color pairs
    match = re.findall(colour_pattern, line)
    if match:
        models[current_model] += match
    print("models:",models)


# Construct output string
output = "  ColourFrom >> {"
for model, countries in models.items():
    for country, color in countries:
        output += f"({model}, {country}) -> {color}, "
output = output[:-2]  # Remove trailing comma and space
output += "}."

# print(output)
solu = "    type Node:= {"
for i in range(len(solutions)):
    solu += solutions[i]
    if(i != len(solutions)-1):
        solu += ","
solu += "}"
print(solu)

# Open the file in read mode
BASE = os.path.dirname(os.path.abspath(__file__))
input ='cluster.idp'

with open(os.path.join(BASE,input), 'r') as file:
    lines = file.readlines()

# Insert the new line at the desired position
position_to_insert = 17
if not lines[position_to_insert - 1].strip():
    lines.insert(position_to_insert - 1, output)  # Adjust index to 0-based

# Solutions
position_to_insert = 2
if not lines[position_to_insert - 1].strip():
    lines.insert(position_to_insert - 1, solu)

print(lines)
# Open the file in write mode and write the modified lines back to the file
with open('/home/jonas/Documents/MP/IDP/Offline/cluster.idp', 'w') as file:
    file.writelines(lines)


with open('/home/jonas/Documents/MP/IDP/Offline/cluster.idp', 'r') as file:
    code = file.read()

kb = IDP.from_str(code)
f = io.StringIO()
with contextlib.redirect_stdout(f):

    kb.execute()

output = f.getvalue()
print(output)