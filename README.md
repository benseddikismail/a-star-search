# A* Search

A* search finds the shortest path between 2 cities given one of the following cost functions:
- segments: find a route with the fewest number of road segments (i.e. edges of the graph).
- distance: find a route with the shortest total distance.
- time: find the fastest route, assuming one drives the speed limit.
- delivery: find the fastest route, in expectation, for a certain delivery driver. Whenever this driver drives on a road with a speed limit ≥ 50 mph, there is a chance that a package will fall out of their truck and be destroyed. They will have to drive to the end of that road, turn around, return to the start city to get a replacement, then drive all the way back to where they were (they won’t make the same mistake the second time they drive on that road).
Consequently, this mistake will add an extra 2·(t<sub>road</sub>+t<sub>trip</sub>) hours to their trip, where t<sub>trip</sub> is the time it took to get from the start city to the beginning of the road, and t<sub>road</sub> is the time it takes to drive the length of the road segment. 
For a road of length _L_ miles, the probability p of the mistake is equal to tanh(_L_/1000) if the speed limit is ≥ 50 mph, and 0 otherwise.This means that, in expectation, it will take t<sub>road</sub> + 2·p·(t<sub>road</sub>+t<sub>trip</sub>) hours to drive on this road.

city-gps.txt contains one line per city, with three fields per line, 
delimited by spaces. The first field is the city, followed by the latitude,
followed by the longitude.

road-segments.txt has one line per road segment connecting two cities.
The space delimited fields are:

- first city
- second city
- length (in miles)
- speed limit (in miles per hour)
- name of highway

> Note that there are mistakes and bugs in the dataset; e.g. not all cities that appear in road-segments.txt have a corresponding line in city-gps.txt.

#### Run
```console
ismail@ismail:~$ python3 ./route.py [start-city] [end-city] [cost-function]
```

### Elements of the search problem
- **Initial state**: start city encompassing all the necessary information about itself and the road it is on such as the distance of the road, the highway (the name of the road), and the speed limit on that road
- **State space**:  cities/highways present in the datasets (each encompassing relevant information)
- **Successor function**: go to the neighboring city/highway with the lowest possible cost
- **Goal state**: destination city with all its elements (e.g., position, time taken to reach the city...)
- **Cost function**: the following are the cost functions influencing the selection of successor states:
    - The distance from the start city to a state
    - The number of road segments between the start city and a state
    - The time taken to traverse the whole distance of the road, driving the speed limit
    - The time taken to deliver all packages. If the speed limit is equal to or over 50 mph, there is a change (probability of dropping a package) that the delivery time is sort of penalized by adding more time (2·(t<sub>road</sub> +t<sub>trip</sub>)) to the trip.  
### Heuristic
The heuristic function is of the same nature as the cost function (segments, time, distance, delivery):
- **Segments**
    - The ratio of the distance between a given city and the goal city, and the maximum road length amongst all road lengths
    - *Admissible* since it is always going to be less than the actual number of road segments between a city and the target city as we are dividing the distance by the maximun road length
    - *Consistent* because the distance is divided by the maximum segment length, so, the estimation cannot get any greater than the actual cost of getting from a city to its successor plus the heuritic from that successor to the destination
- **Distance**
    - The distance between a given city and the goal city. This distance, used to yield all other heuristics, is the actual distance between a city and the goal given their latitudes and longitudes. 
    - *Admissible* and *consistent* since it the exact distance between a city and the destination
- **Time** and **Delivery**
    - The ratio of the distance between a given city and the goal city, and the maximum speed limit
    - *Admissible* and *consistent* since we divide the distance by the maximum speed limit which yields a time that is always less than the actual time it takes to reach the destination from any city, and the time it takes a city to reach its neighboring (successor) city
### A*
Since we know the goal state, this is an informed search problem. The A* search algorithm guarentees to find the complete and optimal path to the destination.  
In principle, the implementation of A* builds a search graph as it goes through the cities/highways. It uses an open list as the fringe to inlude active cities awaiting expansion, and a closed list (a set) to hold all visited nodes with the least f cost that are already part of the path. Depending on the nature of the cost (segments, time, distance, delivery), the f cost is the sum of the cumulative cost to move from the start city to other cities, and the heuristic which is the cost to go from any city to the destination. Because of the outliers in the dataset, if a city does not have a position (latitude, longitude), its heuristic is just 0 and only the g cost is considered. This way, we can ensure that the heuristic is admissible because otherwise the distance between any 2 cities will be far overestimated, given that the geodetic coordinates of one of them is (0, 0) (unknown position).  
The nodes of the graph are cities encompassing relevant information about themselves and the road (e.g., the path from the start city to the current one). Successors yet to be expanded are put in the open list. The successor city with the least f cost is put into the closed list making it part of the path. While the open list (fringe) still holds nodes to be expanded, a node yet to be expanded with a lower f cost than the current successor or a node already in the closed list are skipped. The outliers in the dataset, can lead the heuristics, in case the cost is delivery or segments, to be inconsistent. Thus, if a city is found in the open list (fringe) with a larger f cost, it is replaced in the open list with the version having the lower f cost.
The challenge faced during the implementation of the search algorithm stems from the inconsistencies in the dataset. Hence, to prevent the inadmissibility of the heuristics, only successors with the lowest f cost are considered, and only the g cost is accounted for in case a city's position is missing.  
A tentative solution in the code assigns the positions of the closest neighbors to the goal and start cities in case they do not have a position. However, it is assumed that goal and start cities to be used to test the algorithm have positions that are present in the dataset because assigning neighbouring positions does not really make sense as the whole objective of the search is finding a path between the start and the destination (and not the neighboring cities).  
Future work can touch upon resolving other inconsistencies that may arise from the datasets such as invalid coordinates (latitudes and longitudes), and "cities" that are actually highway intersections.