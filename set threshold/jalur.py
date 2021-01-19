from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from tqdm import tqdm
import time


## select distance measurement
def real_distance(lon1, lat1, lon2, lat2):
    r = requests.get('https://osrm.warungpintar.co/route/v1/driving/{},{};{},{}'.format(lon1,lat1,lon2,lat2))
    res = ast.literal_eval(r.text)
    return res['routes'][0]['legs'][0]['distance'] / 1000 # distance in km


def haversine_distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def create_data_model(df,distance_method):
    """Stores the data for the problem."""
    
    #depo latlong
    tekno = [-6.3336,106.678]
    
    lst = []
    
    #including the depo
    jaraktekno = []
    jaraktekno.append(0) #distance to himself
    for k in range(len(df)):
        jaraktekno.append(distance_method(tekno[1],tekno[0],df['partner_longitude'][k],df['partner_latitude'][k]))
    lst.append(jaraktekno)
    for i in tqdm(range(len(df))):
        temp = []
        temp.append(distance_method(df['partner_longitude'][i],df['partner_latitude'][i],tekno[1],tekno[0]))
        for j in range(len(df)):
            temp.append(distance_method(df['partner_longitude'][i],df['partner_latitude'][i],df['partner_longitude'][j],df['partner_latitude'][j]))
        lst.append(temp)
            
    data = {}
    data['distance_matrix'] = lst
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data


def print_solution(manager, routing, solution):
    """Prints solution on console."""
    total_distance = solution.ObjectiveValue()
    print('Objective: {} km'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = 'Route for vehicle _:\n'
    route_distance = 0
    
    urutan_index = []
    while not routing.IsEnd(index):
        node_index = manager.IndexToNode(index)
        urutan_index.append(node_index)
        
        plan_output += ' {} ->'.format(manager.IndexToNode(index))        
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(manager.IndexToNode(index))
    print(plan_output)
    plan_output += 'Route distance: {}km\n'.format(route_distance)
    
    return urutan_index, total_distance


def jalurkeun(df_csv,number_of_cluster,distance_method):
    """Entry point of the program."""
    df_csv = df_csv[df_csv['result'] == number_of_cluster].reset_index(drop=True)
    # Instantiate the data problem.
    data = create_data_model(df_csv,distance_method)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        urutan_index, total_distance = print_solution(manager, routing, solution)
    
    urutan_index = list(filter(lambda x: x != 0, urutan_index))
    urutan_index = [x - 1 for x in urutan_index]
#     print(urutan_index)

    urutan = pd.DataFrame(urutan_index)
    urutan['urutan'] = urutan.index
    urutan.index = urutan[0]
    del urutan[0]
    
    df = df_csv.merge(urutan,left_index=True, right_index=True).sort_values(by='urutan').reset_index(drop=True)
    
    cls_distance = []
    cls_distance.append({'cluster':number_of_cluster, 'distance_km':total_distance})
    cls_distance = pd.DataFrame(cls_distance)
    
    return df, cls_distance