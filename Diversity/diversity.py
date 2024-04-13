from idp_engine import IDP, Theory
from idp_engine.Parse import TheoryBlock, Structure
from idp_engine.Run import model_expand
from typing import Union, Iterator
import argparse, time
from change_idp_file import runCode, readCode, insertCode, printCode, checkPredFunc, collectSol, collectBaseSol, simMatrix, clustering
class idp(IDP):
    # -> is a function annotation to document the return value for a function
    # code:str means that code is expected to be a string
    # cls means that the method is a class method
    # Union defines that the variable van hold values of different types
    def from_str(cls, code:str) -> "IDP":
        IDP.from_str(cls, code)

    # Iterator is an object
    def model_expand(*theories: Union[TheoryBlock, Structure, Theory],
                 max: int = 10,
                 timeout_seconds: int = 10,
                 complete: bool = False,
                 extended: bool = False,
                 sort: bool = False
                 ) -> Iterator[str]:
        model_expand(theories,max,timeout_seconds,complete,extended,sort)
    
    def check_method(method:str) -> bool:

        valid_methods = ["Offline", "Online1", "Online2", "Clustering"]
        if method in valid_methods:
            return True
        else:
            return False

    def diverse_model_generation(input:str,n:int,k:int,relevant:list,method:str):
        lines = readCode(input)   
        # Delete comments 
        lines = [line for line in lines if '//' not in line]
        # printCode(lines)
        if method == "Clustering":
            foCode = readCode(input)
            output = runCode(foCode)
            # print(output)
            simMat = simMatrix(output,relevant)
            for i in simMat:
                print(i)
            #Clustering
            clustering(simMat,k)
        if method == "Offline":
            output = runCode(lines)
            # print(output)
            isBool = checkPredFunc(lines,relevant)
            n,partSol = collectBaseSol(output,relevant,isBool)
            insertCode(lines,n,k,relevant,partSol,isBool,method)
            # print(partsol)
            # printCode(lines)
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
                    # print(isBool)
                elif i == 2:
                    k=k_orig//n
                    insertCode(lines,i,k,partSol,isBool)
                else:
                    k=i*k_orig//n
                    insertCode(lines,i,k,partSol,isBool)
                
                printCode(lines)
                output = runCode(lines)
                print(output)
                # Collect solutions
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

    if not idp.check_method(method):
        print("Given method does not exist")
    elif goal == None:
        print("All functions are relevant")
    else:
        idp.diverse_model_generation(input,n,k,goal,method)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
