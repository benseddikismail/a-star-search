import sys
import heapq
from math import radians, cos, sin, asin, sqrt, tanh

def parse_dataset(filename):
        with open(filename, "r") as f:
                return [line.split() for line in f.read().rstrip("\n").split("\n")]
        
def parse_cities(filename):

    cities_dict = {
        # city: (latitude, longitude),
    }
    with open(filename, "r") as f:
        for line in f:
            city_name, lat, long = line.split(" ")
            long = long.replace("\n","")
            cities_dict[city_name] = (float(lat), float(long))
    return cities_dict

def get_max_speed_limit(roads):

    max_speed_limit = 0

    for _,_,_,speed_limit,_ in roads:
        max_speed_limit = max(max_speed_limit, int(speed_limit))
    
    return max_speed_limit

def get_max_length(roads):
  
    max_length  = 0

    for _,_,length,_,_ in roads:
        max_length = max(max_length, int(length))
    
    return max_length

def get_city_position(cities, city):
    if city in cities:
        return cities[city]
    else:
        return None

def moves(road, city):
    moves = [] # all possible moves from a city (neighboring cities)
    for city1, city2, length, speed_limit, highway in road:
        neighbor = city1 if city == city2 else city2 if city == city1 else None
        if neighbor:
            moves.append([neighbor, int(length), int(speed_limit), highway])
    return moves

def distance(city1, city2):

    city1_pos, city2_pos = city1.position, city2.position

    lat1, long1 = radians(city1_pos[0]), radians(city1_pos[1])
    lat2, long2 = radians(city2_pos[0]), radians(city2_pos[1])

    #Haversine formula
    d_lon = long2 - long1 
    d_lat = lat2 - lat1
    a = sin(d_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(d_lon / 2)**2
    b = 2 * asin(sqrt(a))
    
    r = 3958.8 #radius of earth in miles (r = 6371 in km)

    return (b*r)

def heuristic(cost, node, goal, max_speed_limit, max_length):
        
    if cost == "segments":
        return distance(node, goal) / max_length
        
    elif cost == "distance":
        return distance(node, goal)

    elif cost in ("time", "delivery"):
        return distance(node, goal) / max_speed_limit


class City():
    def __init__(self, parent, name, position=None):
            self.name = name
            self.parent = parent
            self.position = position
            self.h = self.g = self.f = 0
            self.distance = 0
            self.time = 0
            self.speed_limit = 1
            self.highway = None
            self.delivery_time = 0
            self.path = []

    def __eq__(self, other):
        return (self.position == other.position and self.name == other.name)
    def __lt__(self, other):
        return self.f < other.f
    def __gt__(self, other):
        return self.f > other.f
    def __hash__(self):
        return hash((self.name, self.position))

def search(start, goal, cost):

    roads = parse_dataset("road-segments.txt")
    cities = parse_cities("city-gps.txt")

    max_speed_limit = get_max_speed_limit(roads)
    max_length = get_max_length(roads)

    start_city = City(None, start)
    goal_city = City(None, goal)
    start_city.g = start_city.h = start_city.f = 0
    goal_city.g = goal_city.h = goal_city.f = 0

    open_list = list()
    closed_list = set()

    start_city_pos, goal_city_pos = get_city_position(cities, start_city.name), get_city_position(cities, goal_city.name)

    if start_city_pos and goal_city_pos:
        start_city.position = start_city_pos
        goal_city.position = goal_city_pos
        start_city.h = heuristic(cost, start_city, goal_city, max_speed_limit, max_length)

    elif start_city_pos and not goal_city_pos:  
        start_city.position = start_city_pos    
        min_heuristic = float("inf")
        for move in moves(roads, goal_city.name):
            adj_city = City(None, move[0])
            adj_city.position = get_city_position(cities, adj_city.name)
            if adj_city.position is not None and min_heuristic > heuristic(cost, start_city, adj_city, max_speed_limit, max_length):
                min_heuristic = heuristic(cost, start_city, adj_city, max_speed_limit, max_length)
                goal_city.position = adj_city.position
        start_city.h = min_heuristic

    elif not start_city_pos and goal_city_pos:
        goal_city.position = goal_city_pos 
        start_city.position = (0, 0)

    elif not start_city_pos and not goal_city_pos:
        # closest alternative cities to the start and goal cities
        start_cities, goal_cities = list(), list() 

        for move in moves(roads, start_city.name):
            adj_city = City(None, move[0])
            adj_city.position = get_city_position(cities, adj_city.name)
            if adj_city.position is not None:
                start_cities.append(adj_city)

        for move in moves(roads, goal_city.name):
            adj_city = City(None, move[0])
            adj_city.position = get_city_position(cities, adj_city.name)
            if adj_city.position is not None:
                goal_cities.append(adj_city)
        
        min_heuristic = float("inf")
        for alt_start_city in start_cities:
            for alt_goal_city in goal_cities:
                alt_start_pos = get_city_position(cities, alt_start_city.name)
                alt_goal_pos = get_city_position(cities, alt_goal_city.name)
                if min_heuristic > heuristic(cost, alt_start_city, alt_goal_city, max_speed_limit, max_length):
                    min_heuristic = heuristic(cost, alt_start_city, alt_goal_city, max_speed_limit, max_length)
                    start_city.position = alt_start_pos
                    goal_city.position = alt_goal_pos
        start_city.h = min_heuristic


    heapq.heappush(open_list, start_city)

    while open_list:

        current_city = heapq.heappop(open_list)

        closed_list.add(current_city)

        if current_city == goal_city:
            return (current_city.distance, current_city.time, current_city.delivery_time, current_city.path)

        #get successors
        successors = list()

        for move in moves(roads, current_city.name):
            # move[0] = city_name
            successor_pos = get_city_position(cities, move[0])
            successor_node = City(current_city, move[0], successor_pos)
            successor_node.distance = float(move[1])
            successor_node.speed_limit = float(move[2])
            successor_node.highway = move[3]
            successors.append(successor_node)

        for successor in successors:

            if successor in closed_list:
                continue

            p = 0
            if successor.speed_limit >= 50:
                p = tanh(successor.distance/1000)
            
            t_road = successor.distance/successor.speed_limit
            t_trip = current_city.delivery_time
            successor.delivery_time = t_road + (2*p*(t_road+t_trip))
            
            if cost == "segments":
                successor.g = len(current_city.path) + 1
            elif cost == "distance":
                successor.g = current_city.distance + successor.distance
            elif cost == "time":
                successor.g = current_city.time + (successor.distance/successor.speed_limit)
            else: #delivery
                successor.g = current_city.delivery_time + successor.delivery_time

            if successor.position is not None:
                successor.h = heuristic(cost, successor, goal_city, max_speed_limit, max_length)

            successor.f = successor.g + successor.h

            if cost in ("delivery", "segments"):
                
                city, idx = None, None
                for i, node in enumerate(open_list):
                    if node == successor:
                        city, idx = node, i
                        break

                if city:

                    if successor.f < city.f:

                        open_list.pop(idx)
                        
                        successor.time = current_city.time + successor.distance/successor.speed_limit
                        successor.delivery_time += current_city.delivery_time
                        successor.path = current_city.path + [[successor.name, successor.highway, successor.distance]]
                        successor.distance += current_city.distance
                    
                        heapq.heappush(open_list, successor)
                else:

                    successor.time = current_city.time + successor.distance/successor.speed_limit
                    successor.delivery_time += current_city.delivery_time
                    successor.path = current_city.path + [[successor.name, successor.highway, successor.distance]]
                    successor.distance += current_city.distance
                    
                    heapq.heappush(open_list, successor)
            else:

                successor.time = current_city.time + successor.distance/successor.speed_limit
                successor.delivery_time += current_city.delivery_time
                successor.path = current_city.path + [[successor.name, successor.highway, successor.distance]]
                successor.distance += current_city.distance
                
                heapq.heappush(open_list, successor)
                
            #heapq.heappush(open_list, successor)
            

def get_route(start, end, cost):
    
    """
    Find shortest driving route between start city and end city
    based on a cost function.

    Return a dictionary having the following keys:
        -"route-taken" : a list of pairs of the form (next-stop, segment-info), where
           next-stop is a string giving the next stop in the route, and segment-info is a free-form
           string containing information about the segment that will be displayed to the user.
           (segment-info is not inspected by the automatic testing program).
        -"total-segments": an integer indicating number of segments in the route-taken
        -"total-miles": a float indicating total number of miles in the route-taken
        -"total-hours": a float indicating total amount of time in the route-taken
        -"total-delivery-hours": a float indicating the expected (average) time 
                                   it will take a delivery driver who may need to return to get a new package

    """
    
    total_distance, total_time, total_delivery_time, path = search(start, end, cost)

    route_taken = []

    for (city, highway, distance) in path:
        route_taken.append((city, highway + " for " + str(int(distance)) + " miles"))

    return {"total-segments" : len(route_taken), 
            "total-miles" : total_distance, 
            "total-hours" : total_time, 
            "total-delivery-hours" : total_delivery_time, 
            "route-taken" : route_taken}


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise(Exception("Error: expected 3 arguments"))

    (_, start_city, end_city, cost_function) = sys.argv
    if cost_function not in ("segments", "distance", "time", "delivery"):
        raise(Exception("Error: invalid cost function"))
    
    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    for step in result["route-taken"]:
        print("   Then go to %s via %s" % step)

    print("\n          Total segments: %4d" % result["total-segments"])
    print("             Total miles: %8.3f" % result["total-miles"])
    print("             Total hours: %8.3f" % result["total-hours"])
    print("Total hours for delivery: %8.3f" % result["total-delivery-hours"])


