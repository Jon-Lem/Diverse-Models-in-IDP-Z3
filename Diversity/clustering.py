import numpy as np
import itertools
from sklearn_extra.cluster import KMedoids
import re
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt

distcheck = 0

def saveModel(output,pattern):
    models = []
    for line in output.split("\n"):
        match = re.match(pattern,line)
        if match:
            # print(line)
            try: # If predicate
                model = eval("[" + match.group(1) + "]")
            except: # If function
                model = re.findall( r'->\s*(\w+)', match.group(1))
                # print(model)
                # print(len(model))
                # exit()
            if model == []:
                model = line.split(':=')[1].split('.')[0].strip()
            # print(model)
            models.append(model)
    return models

def simMatrix(output,goal):
    for k in range(len(goal)):
        pattern = re.escape(goal[k]) + r' := {(.*)}'
        models = saveModel(output,pattern)
        if len(models) == 0:
            pattern = re.escape(goal[k]) + r' := (.*)'
            models = saveModel(output,pattern)
        # print(models)
        # exit()
        if k==0:
            simMat = [[0 for _ in range(len(models))] for _ in range(len(models))]
        for i in range(len(models)):
            for j in range(len(models)):
                # distance = len(set(models[j]) - set(models[i]))
                if not isinstance(models[i], list):
                    distance = 1 if models[i] != models[j] else 0
                else:
                    distance = sum(x != y for x, y in zip(models[i], models[j]))
                if k==0:
                    simMat[i][j] = distance
                else:
                    simMat[i][j] += distance
                # print(f"simMat[{i}][{j}] = {simMat[i][j]}")
    
    return simMat

def searchNKmodels(simMat,n,k):
    solutions_candidates = []
    n_models = len(simMat)
    print('Number of models: ',n_models)
    distance_treshold = (k/((n-1)*n*0.5))
    print('Distance treshold:',distance_treshold)
    solutions = []
    solution_space = []
    for i in range(n_models):
        number_of_connections = 0
        for j in range(n_models):
            if(simMat[i][j] >= distance_treshold):
                number_of_connections += 1
                if i not in solutions: solutions.append(i)
                if j not in solutions: solutions.append(j)
        solution_space.append(solutions)
        solutions = [] 
    # for i in range(n_models):
    #     print(solution_space[i])
    # exit()

    for sol in solution_space:
        if len(sol) >= n:
            combinations = list(itertools.combinations(sol[1:], n-1))
            # print('\nModel ',sol[0])
            # print('==========\n')
            for combo in combinations:
                # print('Combo',list(combo))
                # print(sol[0])
                solutions_candidates = list(combo)
                solutions_candidates.append(sol[0])
                # print(solutions_candidates)
                if distCheck(simMat,solutions_candidates,k):
                    return sorted(solutions_candidates)
        else: continue
    print('Solution is not satisfiable')
    exit()


def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)

def translate(result,valdict):
    dewey=[]
    if isinstance(result, list):
        for i in result:
            dewey.append(valdict[i])
    else:
        dewey.append(valdict[result])
    # print(f'Result:\n {result}')
    # print(f'Dewey Encoding:\n {dewey}')

    return dewey

def distCheck(simMat,solutions,k):
    # print(solutions)
    sum_distance = 0
    for i in range(len(solutions)):
        for j in range(len(solutions)):
            a = solutions[i]
            b = solutions[j]
            sum_distance += simMat[a][b]
            # print(f'(s{a+1},s{b+1}) -> {simMat[a][b]}')
    if(sum_distance//2 >= k):
        # print("distCheck 1")
        # print(solutions)
        # print(sum_distance/2)
        global distcheck
        distcheck=1
        return True
    else: 
        # print("distCheck 0")
        return False
    
def prettyPrint(simMat,solutions,k):
    total_distance = 0
    dist = []
    for i in range(len(solutions)):
        for j in range(len(solutions)):
            a = solutions[i]
            b = solutions[j]
            dist.append(f'(s{a+1},s{b+1}) -> {simMat[a][b]}')
            total_distance += simMat[a][b]
    distance = ','.join(dist)
    print('distance := {' + distance + '}.')
    print('total distance :=',total_distance/2)
    if total_distance/2 < k:
        print('Solution is not satisfiable')
        exit()
    print(f'k := {k}.')

def clusterComp(clusters:list,i:int,j:int,l:list):
    if clusters[i] != clusters[j] and l == []:
        return True
    elif clusters[i] != clusters[j] and l != [] :
        for item in l:
            if(clusters[j] == clusters[item]):
                return False
        return True
    else:
        return False

def clustering(simMat,k,n,method,linkage_type):
    print(f'distance_threshold = {k//((n-1)*n*0.5)}')
    if method == 'Clustering' or method == "Single" or method == "Complete":
        # linkage_type ='complete'
        model = AgglomerativeClustering(
        metric='precomputed',
        n_clusters=None,
        distance_threshold = k//((n-1)*n*0.5), #Wilt dat elke cluster een afstand van 7 met elkaar heeft
        linkage=linkage_type
        ).fit(simMat)
        print(f" Number of clusters: {model.n_clusters_}")
        if(model.n_clusters_ == 1):
            print('Solution is not satisfiable')
            exit()
        clusters = list(model.labels_)

    elif method == 'Kmedoids':
        kmedoids = KMedoids(n_clusters=n, random_state=0, metric='precomputed')
        clusters = kmedoids.fit_predict(simMat)
        print("Cluster Labels:")
        print(clusters)
    
    # print(set(list(model.labels_)))
    # solutions = [list(model.labels_).index(x) for x in set(list(model.labels_)) ]
    # solutions = solutions[:n]

    # plt.title("Hierarchical Clustering Dendrogram")
    # x = squareform(simMat)
    # temp = linkage(x, linkage_type)
    # dendrogram(temp, above_threshold_color="green", color_threshold=k//n , orientation='right')
    # plt.show()

    # plt.title("Hierarchical Clustering Dendrogram")
    # # plot the top three levels of the dendrogram
    # plot_dendrogram(model, truncate_mode="level", p=3)
    # plt.xlabel("Number of points in node (or index of point if no parenthesis).")
    # plt.show()

    solutions = []
    for i in range(len(clusters)):
        l = []
        for j in range(len(clusters)):
            if clusterComp(clusters,i,j,l): 
                if(simMat[i][j] >= (k/((n-1)*n*0.5))):
                    # print(f'(s{i},s{j}) -> {simMat[i][j]}')
                    if i not in solutions: solutions.append(i)
                    if j not in solutions: solutions.append(j)
                    l.append(j)
        # print(l)
    # print(solutions)
    # exit()
    n_solutions=solutions[:n]
    i = 0
    while not distCheck(simMat,n_solutions,k) and len(solutions) > n+i:
        i+=1
        n_solutions = solutions[i:n+i]
    # print(solutions)
    # print(n_solutions)
    solutions = n_solutions
    if(distcheck==0):
        print('Solution is not satisfiable')
        exit()
    prettyPrint(simMat,solutions,k)

    return