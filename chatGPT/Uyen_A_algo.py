import heapq

# Define a heuristic function that calculates the estimated cost between two points.
# Here, it's the Euclidean distance squared between two points.
def heuristic(a, b):
    return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2


def astar(array, start, goal):
    # Define the possible neighbor movements, including diagonal movements.
    neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]

    # Initialize sets and dictionaries to keep track of visited nodes, their scores, and the path.
    close_set = set()
    came_from = {}
    gscore = {start:0} # Initialize the g score of the start node
    fscore = {start:heuristic(start, goal)} # Initialize the f score of the start node
    oheap = []


    heapq.heappush(oheap, (fscore[start], start))
    
    # Main A* algorithm
    while oheap:
        # Pop the node with the lowest fscore from the priority queue
        current = heapq.heappop(oheap)[1]

        # If the current node is the goal, reconstruct and return the path
        if current == goal:
            data = [] # Reconstruct the path
            while current in came_from: 
                data.append(current)
                current = came_from[current] # Move to the previous node
            return data

        # Add the current node to the set of evaluated nodes
        close_set.add(current) # Mark the current node as evaluated

        # Iterate through neighbors of the current node
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j   # Calculate the neighbor's coordinates    
            # Calculate tentative g score for the neighbor
            tentative_g_score = gscore[current] + heuristic(current, neighbor)

            # Check if the neighbor is within the bounds of the array
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    # Check if the neighbor is an obstacle (1)
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    # Skip if the neighbor is out of bounds in the y direction
                    continue
            else:
                # Skip if the neighbor is out of bounds in the x direction
                continue

            # If the neighbor has already been evaluated and the new score is not better, skip
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            # If the new score is better or the neighbor has not yet been evaluated
            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                # Update scores and add the neighbor to the priority queue
                came_from[neighbor] = current # Update the path
                gscore[neighbor] = tentative_g_score # Update the g score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal) # Update the f score
                heapq.heappush(oheap, (fscore[neighbor], neighbor)) # Add the neighbor to the priority queue

    # Return False if no path is found
    return False




### improved version of the A* algorithm
import heapq

def heuristic(a, b):
    # Use Manhattan distance as a heuristic for faster computation
    return abs(b[0] - a[0]) + abs(b[1] - a[1])

def astar(array, start, goal):
    # Define possible neighbor movements, including diagonal movements
    neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
    
    # Initialize sets and dictionaries
    closed_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}
    open_set = []

    # Use heapq to make the open_set act as a priority queue
    heapq.heappush(open_set, (fscore[start], start))
    
    while open_set:
        # Pop the node with the lowest fscore from the priority queue
        current_fscore, current = heapq.heappop(open_set)

        # If the current node is the goal, reconstruct and return the path
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]  # Reverse the path to get it from start to goal

        # Add the current node to the set of evaluated nodes
        closed_set.add(current)

        # Iterate through neighbors of the current node
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j

            # Check if the neighbor is within the bounds of the array and is not an obstacle
            if 0 <= neighbor[0] < array.shape[0] and 0 <= neighbor[1] < array.shape[1] and array[neighbor[0]][neighbor[1]] == 0:
                tentative_gscore = gscore[current] + 1  # Assuming each step costs 1

                # If the neighbor has already been evaluated and the new score is not better, skip
                if neighbor in closed_set and tentative_gscore >= gscore.get(neighbor, 0):
                    continue

                if tentative_gscore < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in open_set]:
                    # Update scores and add the neighbor to the priority queue
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_gscore
                    fscore[neighbor] = tentative_gscore + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (fscore[neighbor], neighbor))
                
    return False