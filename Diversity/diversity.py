from idp_engine import IDP
import argparse, time
from change_idp_file import *
from clustering import *
from ordering import *
from relevance import *

relevant = ''

class idp(IDP):    
    def check_method(method:str) -> bool:
        valid_methods = ["Base", "Offline", "Online1", "Online2", "Clustering", "Ordering","Relevance"]
        if method in valid_methods:
            return True
        else:
            return False

    def check_args(input:str,method:str,goal:list) -> None | list:

        if not idp.check_method(method):
            print("Error: Given method does not exist")
            exit()
        elif not goal:
            lines = readCode(input)
            goal = completeFunc(lines,goal)
            return goal

    def diverse_model_generation(input:str,n:int,k:int,relevant:list,method:str):
        lines = readCode(input)   
        # Delete comments 
        lines = [line for line in lines if '//' not in line]
        checkFunc(lines,relevant)
        # printCode(lines)
        if method == "Base":
            output = runCode(lines)
            print(output)
        if method == "Relevance":
            file = 'priority.txt'
            relevance_dict = getOrdering(file)
            distTheory(relevance_dict,'Security',relevant)
        if method == "Ordering":
            # print(relevant)
            output = runCode(lines)
            print(output)
            relevant = priorityOrdering(relevant)
            print(relevant)
            dictlist,deweylist = ordering(output,relevant)
        if method == "Clustering":
            output = runCode(lines)
            # print(output)
            simMat = simMatrix(output,relevant)
            for i in simMat:
                print(i)
            #Clustering
            clustering(simMat,k,n)
        if method == "Offline":
            output = runCode(lines)
            # print(output)
            isBool = checkPredFunc(lines,relevant)
            n,partSol = collectBaseSol(lines,output,relevant,isBool)
            insertCode(lines,n,k,relevant,partSol,isBool,method)
            # print(partsol)
            printCode(lines)
            output = runCode(lines)
            print(output)
        if method == "Online1":
            insertCode(lines,n,k,relevant)
            printCode(lines)
            output = runCode(lines)
            print(output)
        if method == "Online2":
            k_orig = k
            for i in range(1,n+1):
                if i == 1:
                    k=0
                    isBool = checkPredFunc(lines,relevant)
                    insertCode(lines,i,k,relevant)
                    # printCode(lines)
                    # print(isBool)
                elif i == 2:
                    k=k_orig//n
                    insertCode(lines,i,k,relevant,partSol,isBool,method)
                    # printCode(lines)
                else:
                    k=i*k_orig//n
                    insertCode(lines,i,k,relevant,partSol,isBool,method)
                # print('==============')
                # print(i)
                # print('===LINES===')
                printCode(lines)
                output = runCode(lines)
                print(output)
                # Collect solutions
                if(i != n):
                    partSol = collectSol(output,relevant,isBool)                  
                # Update code with new solutions
            
def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('input',type=str,help="Input IDP file")
    parser.add_argument('-n','--n',type=int,help="number of solutions")
    parser.add_argument('-k','--k',type=int,help="total distance k")
    parser.add_argument('method',type=str,help="Method of calculating diversity, choice between: Offline, Online1, Online2, Clustering")
    parser.add_argument('goal',nargs='*', type=str ,help="target of the diversity")    
    args = parser.parse_args()

    input = args.input
    n = args.n 
    k = args.k  
    goal = args.goal 
    method = args.method 
    # print(f"arguments: {input} {n} {k} {goal} {method}")   
    # result = idp.check_args(input,method,goal)
    result = idp.check_args(input,method,goal)
    if result:
        goal = result
    # print(f"arguments: {input} {n} {k} {goal} {method}") 
    idp.diverse_model_generation(input,n,k,goal,method)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
