# Programma dat zoekt naar n oplossingen die een totale afstand hebben van k
# Dus k is de som van d(sx,sy) voor sx,sy deel van de oplossingen verzameling

import re
import var
from typing import Iterator
from print import *


def createBlock(lines:list,block):
    target = 'procedure'
    index = indexsearch(lines,target)
    if block == 'struct':
        block = ['structure {\n','}\n']
    elif block == 'theory':
        block = ['theory {\n','}\n']
    lines[index:index] = block
    return lines

def completeFunc(lines,relevant:list) -> Iterator[str]:
    target = "vocabulary"
    begin_voc = indexsearch(lines,target)
    end_voc = indexsearch(lines[begin_voc:],"}") + begin_voc    
    voc_lines = lines[begin_voc:end_voc]
    # print(voc_lines)
    # pattern = r'^\s*(\w+)\s*:\s*\w'
    pattern = r'^\s*(\w+)\s*:\s*'
    relevant= [re.match(pattern, line).group(1) for line in voc_lines if re.match(pattern, line)]
    # print(relevant)
    return relevant

def checkFunc(lines:list,relevant:list) -> None:
    target = "vocabulary"
    begin_voc = indexsearch(lines,target)
    end_voc = indexsearch(lines[begin_voc:],"}") + begin_voc
    for i in range(len(relevant)):
        count = 0
        pattern = r'\b' + re.escape(relevant[i]) + r'\b'
        for line in lines[begin_voc:end_voc]:
            if re.search(pattern, line):
                count+=1
        if count == 0:
            print(f"Error: function '{relevant[i]}' could not be found")
            exit()

def reformat(lines:list,relevant:list):
    # print(relevant)
    # print(lines)
    target = "structure"
    begin_struct = indexsearch(lines,target)
    end_struct = indexEndofBlock(lines,begin_struct)
    for i in range(len(relevant)):
        j=begin_struct
        while j < end_struct:
            if(relevant[i] in lines[j] and '}' not in lines[j]):
                k=j
                while '}' not in lines[k] and k < end_struct:
                    k+=1
                    lines[j] = lines[j].replace('\n','') + lines[k]
                lines=lines[:j+1]+lines[k+1:]
            j+=1
    return lines

def checkConstants(lines:list,relevant:list):
    for i in range(len(relevant)):
        target=f"{relevant[i]}"
        index = indexsearch(lines,target)  
        if '()' in lines[index]:
            var.cte[i] = 1

# Haal de belangrijkste 
def dist_expr(relation:str,goal:str) -> str:
    relation = relation.split("->")[0].strip().split("*")
    relation= [i.strip() for i in relation]
    relation = [(x,relation.count(x)) for x in set(relation)]
    dist_theory = ''
    for word,count in relation:
        element = ','.join([f"{word}__{i}" for i in range(count)])
        if count > 1:
            dist_theory += f"#{{{element} in {word}: {goal}(solution__x,{element}) ~= {goal}(solution__y,{element})}}/{count}"
        elif '()' in word:
            dist_theory += f'(if {goal}(solution__x) ~= {goal}(solution__y) then 1 else 0)'
        else:
            dist_theory += f"#{{{element} in {word}: {goal}(solution__x,{element}) ~= {goal}(solution__y,{element})}}"
    return dist_theory

def indexEndofBlock(lines:list,index:int):
    close = indexsearch(lines[index:],"}") + index
    if indexsearch(lines[index:],"{") == -1:
        return close
    open = indexsearch(lines[index:],"{") + index
    old_close = close
    while (old_close > open):
        index = old_close+1
        new_close = indexsearch(lines[index:],"}") + index
        if new_close > old_close and old_close > open:
            close = new_close
            break
        old_close = new_close
        if indexsearch(lines[index:],"{") == -1:
            break
        open = indexsearch(lines[index:],"{") + index
    end_theory = close
    return end_theory

def insertCode(lines:list,n:int,k:int,goal:list,partSol=None,isBool=None,method=None,dist_theory_=None,n_orig=None):
    # Create 'type solution'
    type_sol = "type solution := {"
    for i in range(1,n):
        type_sol += f"s{i},"
    type_sol+=f"s{n}" + "}\n"

    # If no structure present create it and modify procedure
    target = "structure"
    begin_struct = indexsearch(lines,target)
    if begin_struct == -1:
        # Create Structure
        lines = createBlock(lines,block='struct')
        target="structure"
        begin_struct = indexsearch(lines,target)
        # Update main procedure
        target="model_expand"
        for l in range(len(lines)):
            if target in lines[l]:
                # print(lines[l])
                comma_idx = indexsearch(lines[l],',')
                if(comma_idx != -1):
                    lines[l] = lines[l][:comma_idx] + ',S' + lines[l][comma_idx:]
                else:
                    comma_idx = indexsearch(lines[l],')')
                    lines[l] = lines[l][:comma_idx] + ',S' + lines[l][comma_idx:]
                # print(lines[l])
    end_struct = indexsearch(lines[begin_struct:],"}") + begin_struct

    # Create a theory for k
    k_theory = f"k() = {k}.\n"

    if(isBool != None and method == "Online2"):
        # Update type solution
        target="type solution"
        index = indexsearch(lines,target)
        lines[index] = type_sol
        # Update partial solutions
        # print(partSol)
        for i in range(len(partSol)):
            target="theory"
            begin_theory = indexsearch(lines,target)
            end_theory = indexEndofBlock(lines,begin_theory)
            index = indexsearch(lines[begin_struct:end_struct],f'{goal[i]} :=')
            # If relevant domain is already present in the structure, copy it for the newly added solutions
            if index != -1:
                # print(f'goal[{i}]: {goal[i]}')
                index += begin_struct
                # If it's a constant, take the last value of the constant and copy it to n solutions
                if var.cte[i]:
                    # index += begin_struct
                    value_cte = lines[index].split('->')[-1].split('}.')[0].strip()
                    struct_cte_values = f"{goal[i]} := {{"
                    for j in range(1,n):
                        struct_cte_values += f"s{j} -> {value_cte}, "
                    struct_cte_values+=f"s{n} -> {value_cte} " + "}.\n"
                    # print(struct_cte_values)
                    lines[index] = struct_cte_values
                    continue
                # Find all the tuples in the structure and update them with the correct solution
                # Make copies of the existing relevant domain structure for each of the new solution 
                tuples_pattern = re.compile(r'\((.*?)\)')
                tuples = tuples_pattern.findall(lines[index])
                # print(tuples)
                formatted_tuples = []
                if lines[index].strip().startswith(f"{goal[i]} := {{(s"):
                    for j in range(1,n+1):
                        formatted_tuples += [f"(s{j},{t.split(',',1)[1]})" for t in tuples]
                    func_struct = ",".join(formatted_tuples)
                    lines[index] = f"{goal[i]} := {{" + func_struct + "}."
                    continue
                else:
                    continue
            if(partSol[i] == '.'):
                continue
            # If a partial solution is already present, update it
            if(indexsearch(lines[begin_struct:end_struct],partSol[i].split('{')[0]) != -1):
                # print(f'partSol[{i}] function: {partSol[i].split("{{")[0]}')
                index = indexsearch(lines[begin_struct:end_struct],partSol[i].split('{')[0]) + begin_struct
                lines[index] = partSol[i]
            elif(indexsearch(lines[begin_theory:end_theory],partSol[i].split('&')[0]) != -1):
                # print(f'partSol[{i}] predicate: {partSol[i].split("&")[0]}')
                index = indexsearch(lines[begin_theory:end_theory],partSol[i].split('&')[0]) + begin_theory
                lines[index] = partSol[i]
                # print('partSol',lines[index])
            # If no partial solution is yet present (distinguish between predicates and functions)
            elif(isBool[i]):
                target="theory"
                index = indexsearch(lines,target)+1
                lines.insert(index,partSol[i])
            else:
                target="structure"
                index = indexsearch(lines,target)+1 
                lines.insert(index,partSol[i])
        # Update the value of k
        target = "k() ="
        index = indexsearch(lines,target)
        lines[index] = k_theory
        return

    k_voc = "k: () -> Real\n"
    dist_voc = "distance: solution * solution -> Int\n"
    k_dist_theory = "sum{{distance(solution__x,solution__y) | solution__x,solution__y in solution: solution__x ~= solution__y }}/2 >= k().\n"

    # Update predicate/function and create new distance theory 
    dist_theory = "!solution__x,solution__y in solution: distance(solution__x,solution__y) = "   
    cardinal = []
    first = True
    idx=0
    for i in range(len(goal)):
        # Search for relevant function/variable in the vocabulary
        target=f"{goal[i]}"
        index = indexsearch(lines,target)
        # Save the index of the first relevant function/variable
        if first:
            idx = index
            first = False
        # Append the distance function theory with Hamming distances
        cardinal.append(dist_expr(lines[index].split(':')[1],goal[i]))
        # Update the existing vocabulary of relevant problem domain
        if '()' in lines[index]:
            lines[index] = lines[index].replace("()", "solution")
            var.cte[i] = 1
            # print(lines[index])            
        else:
            lines[index] = lines[index].split(':')[0] + ": solution *" + lines[index].split(':')[1]
        # print(lines[index])

    # Assemble the entire distance definition
    dist_theory += "+".join(cardinal) + '.\n'
    if method == 'Relevance' and dist_theory_ != None:
        dist_theory = dist_theory_
    # print(dist_theory)

    # Insert the new vocabulary lines
    lines.insert(idx,type_sol)
    if method == 'Offline':
        lines.insert(index+2,'k_dist_set: solution-> Bool\n')
        lines.insert(index+2,'n: () -> Int\n')
    lines.insert(index+2,k_voc)
    lines.insert(index+2,dist_voc)

    # Update existing theory with solution type
    target="theory"
    index = indexsearch(lines,target)
    end_theory = indexEndofBlock(lines,index)
    for i in range(len(goal)):
        target="theory"
        index = indexsearch(lines,target)
        # print(goal[i])
        # Find all the theory lines with the relevant domain in it
        func_theory_idx = [j for j in range(index, end_theory) if goal[i] in lines[j]]
        # print(func_theory_idx)
        pattern = r'\b' + re.escape(goal[i]) + r'\s*\((.*?)\)'
        for j in func_theory_idx:
            # print(lines[j])
            if f'{goal[i]}()' in lines[j]:
                lines[j] = re.sub(pattern, re.escape(goal[i]) + r'(solution__0)', lines[j])
                # print(lines[j])
            else: 
                lines[j] = re.sub(pattern, re.escape(goal[i]) + r'(solution__0, \1)', lines[j])
            if "!solution__0 in solution:" not in lines[j]:
                lines[j] = "!solution__0 in solution:" + lines[j]

    # Insert the k and distance theory lines
    if method == 'Offline':
        lines.insert(end_theory,'#{solution__0 in solution: k_dist_set(solution__0)} = n().\n')
        lines.insert(end_theory,f'n() = {n_orig}.\n')
    lines.insert(end_theory,k_theory)
    lines.insert(end_theory,k_dist_theory)
    lines.insert(end_theory,dist_theory)

    # Update the structure, if relevant functions present
    # print(cte)
    for i in range(len(goal)):
        target = "structure"
        begin_struct = indexsearch(lines,target)
        end_struct = indexsearch(lines[begin_struct:],"}") + begin_struct
        index = indexsearch(lines[begin_struct:end_struct],goal[i])
        if index == -1:
            continue
        else: index += begin_struct
        # print(indx)
        if var.cte[i]:
            value_cte = lines[index].split(':=')[1].strip().strip('.')
            struct_cte_values = f"{goal[i]} := {{"
            for j in range(1,n):
                struct_cte_values += f"s{j} -> {value_cte}, "
            struct_cte_values+=f"s{n} -> {value_cte} " + "}.\n"
            lines[index] = struct_cte_values
            continue
        tuples_pattern = re.compile(r'\((.*?)\)')
        tuples = tuples_pattern.findall(lines[index])
        # print(tuples)
        formatted_tuples = []
        for j in range(1,n+1):
            formatted_tuples += [f"(s{j},{t})" for t in tuples]
        # print(formatted_tuples)
        func_struct = ",".join(formatted_tuples)
        lines[index] = f"{goal[i]} := {{" + func_struct + "}."  
    # printCode(lines)
    # exit()

    if(isBool != None and method == "Offline"):
        for i in range(len(isBool)):
            if(isBool[i]):
                target="theory"
                index = indexsearch(lines,target)+1
                if index == 0:
                    # Create Theory
                    lines = createBlock(lines,block='theory')
                    target="theory"
                    index = indexsearch(lines,target)+1
            else:
                target="structure"
                index = indexsearch(lines,target)+1
                if index == 0:
                    # Create Structure
                    lines = createBlock(lines,block='struct')
                    target="structure"
                    index = indexsearch(lines,target)+1
            lines.insert(index,partSol[i])

    return 

def checkPredFunc(lines:list,relevant:list) -> Iterator[int]:
    isBool = []
    for rel in relevant: 
        index = indexsearch(lines,rel)
        # print(lines[index])
        range = lines[index].split("->")[1].strip()
        if(range == "Bool"):
            isBool.append(1)
        else:
            isBool.append(0)

    return isBool

def collectSol(output:str,relevant:list,isBool:list): # Neem altijd de eerste oplossing
    partSol = []
    for i in range(len(relevant)):
        # print(f'rel: {relevant[i]}')
        # print('===OUTPUT===')
        # print(output)
        for line in output.split("\n"):
            index = line.find(relevant[i])
            if index != -1:
                break
        # print(f"===LINE===\n {line}")
        # print(f'===INDEX===\n {index}')
        if isBool[i] == 1:
            tuples_pattern = re.compile(r'\((.*?)\)')
            tuples = tuples_pattern.findall(line)
            # print(tuples)
            formatted_tuples = [f"{relevant[i]}({t})" for t in tuples]
            # print(f'formatted_tuples: {formatted_tuples}')
            partsol = " & ".join(formatted_tuples)
            partsol = partsol + "."
            # print(partsol)    
        else:
            # print(relevant[i])
            # print(line)
            partsol = f'{relevant[i]} >> ' + line.split(":=")[1]
        partSol.append(partsol)
    # print(f'partSol:\n {partSol}')
    if partSol[i].strip() == '.':
        print("Error: cannot satisfy given parameters. Change 'n' or 'k' .")
        exit()
    return partSol

def collectBaseSol(lines:list,output:str,relevant:list,isBool:list) -> tuple[int,Iterator[str]]:
    partSol = []
    for i in range(len(relevant)):
        # Als het al in de struct staat moet je niets doen
        target = "structure"
        begin_struct = indexsearch(lines,target)
        end_struct = indexsearch(lines[begin_struct:],"}") + begin_struct
        index = indexsearch(lines[begin_struct:end_struct],relevant[i])
        if index != -1:
            partSol.append("\n")
            continue
        n = 0
        # If already in the struct change it to partial interpretations
        partsol = f'{relevant[i]} >> {{' if isBool[i] == 0 else ''
        for line in output.split('\n'):
            target = "Model"
            if line.strip().startswith(target):
                n+=1
                continue
            target = f"{relevant[i]}"
            if line.strip().startswith(target): 
                # print('===LINE===\n',line)     
                if isBool[i] == 1:
                    tuples_pattern = re.compile(r'\((.*?)\)')
                    tuples = tuples_pattern.findall(line)
                    # print(line)
                    # print(tuples)
                    formatted_tuples = [f"{relevant[i]}(s{n}, {t})" for t in tuples]
                    # print(formatted_tuples)
                    if formatted_tuples == []:
                        part_sol = ''
                        partsol += part_sol + "   "
                        continue
                    part_sol = " & ".join(formatted_tuples)
                    partsol += part_sol + " & "
                    # print(partsol)    
                else:
                    result_pattern = r"(\b\w+(?:,\w+)?)\s*->\s*(\w+)"
                    match = re.findall(result_pattern,line)
                    formatted_tuples = [f"(s{n},{domain}) -> {range}" for domain,range in match]
                    # print(formatted_tuples)
                    #If it is a variable
                    if formatted_tuples == []:
                        range_ = line.split(':=')[1].strip().strip('.')
                        part_sol = f's{n} -> {range_}'
                        # print(part_sol)
                        partsol += part_sol + " , "
                        continue
                    part_sol = ", ".join(formatted_tuples)
                    partsol += part_sol + " , "
                    # print(partsol)
        if partsol.strip() == '':
            partSol.append(partsol)
            continue
        # Remove the space and the symbol
        partsol = partsol[:-2]+ '}.' if isBool[i] == 0 else  partsol[:-2]+'.'
        partSol.append(partsol)
        # print(partSol)
    # exit()
    return n,partSol




