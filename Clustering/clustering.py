# Programma dat de oplossingen verdeelt in clusters
# gegeven een input idp bestand en afstand k tussen elk paar van de oplossing onderling
# Alle oplossingen voldoen als nu de minimale afstand groter is dan k tussen elk paar van oplossingen

from idp_engine import IDP
import contextlib, argparse
import os, time , io, re
from sklearn.cluster import AgglomerativeClustering

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

def simMatrix(output,goal):

    qpos = []
    pattern = re.escape(goal) + r' := {(.*)}'
    for line in output.split("\n"):
        match = re.match(pattern,line)
        if match:
            try:
                queens = eval("[" + match.group(1) + "]")
            # else: queens = "[" + match.group(1) + "]"
            except:
                queens = re.findall( r'->\s*(\w+)', match.group(1))
                # print(queens)
                # print(len(queens))
                # exit()
            qpos.append(queens)
    # print(qpos)

    simMat = [[0 for _ in range(len(qpos))] for _ in range(len(qpos))]
    for i in range(len(qpos)):
        for j in range(len(qpos)):
            # distance = len(set(qpos[j]) - set(qpos[i]))
            distance = sum(x != y for x, y in zip(qpos[i], qpos[j]))
            simMat[i][j] = distance
            # print(f"simMat[{i}][{j}] = {simMat[i][j]}")
    
    return simMat

def clustering(simMat,k):
    model = AgglomerativeClustering(
    metric='precomputed',
    n_clusters=None,
    distance_threshold = k, #Wilt dat elke cluster een afstand van 7 met elkaar heeft
    linkage='complete'
    ).fit(simMat)
    print(model.labels_)
    print(f" Number of clusters: {model.n_clusters_}")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('input',type=str,help="Input IDP file")
    parser.add_argument('k',type=int,help="distance k between each cluster")
    parser.add_argument('goal',type=str,help="target of the diversity")
    args = parser.parse_args()

    input = args.input
    foCode = readCode(input)
    output = runIDP(foCode)
    # print(output)
    simMat = simMatrix(output,args.goal)
    for i in simMat:
        print(i)
    #Clustering
    clustering(simMat,args.k)

    #Totale afstand is dus k = distance_treshold * #clusters

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))