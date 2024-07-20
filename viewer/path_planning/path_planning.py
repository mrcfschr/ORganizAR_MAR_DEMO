# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import open3d as o3d
import torch
import pdb
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

OBSTACLE_HEIGHT = 0.2
def get_floor_grid(floor_points: np.ndarray,z_mean, grid_width_resolution:int = 100):
    threshold = z_mean+OBSTACLE_HEIGHT
    #get the bounding box of floor_points
    max_x = floor_points[:,0].max()
    min_x = floor_points[:,0].min()
    max_y = floor_points[:,1].max()
    min_y = floor_points[:,1].min()
    #calculate the voxel size:
    class BoundingBox:
        def __init__(self, min_x:int,min_y:int,max_x:int,max_y:int):
            self.min_point = (min_x,min_y)
            self.max_point = (max_x,max_y)

        @property
        def width(self):
            return self.max_point[0]-self.min_point[0]
        @property
        def height(self):
            return self.max_point[1] - self.min_point[1]

    bb = BoundingBox(min_x, min_y, max_x,max_y)
    voxel_size = min(bb.width,bb.height)/grid_width_resolution
    width_res = int(np.ceil(bb.width/voxel_size))
    height_res = int(np.ceil(bb.height/voxel_size))

    def coordinate_to_grid(x:float, y:float, z:float)->(int,int):
        return (
            int((x-bb.min_point[0])//voxel_size),
            int((y-bb.min_point[1])//voxel_size)
        )

    def grid_to_coordinate(x:int , y:int)->(float,float, float):
        return (
            x*voxel_size+bb.min_point[0],
            y*voxel_size+bb.min_point[1],
            z_mean+OBSTACLE_HEIGHT
        )

    mask = floor_points[:,2]>threshold
    floor_points = floor_points[mask]


    grid = np.zeros((width_res, height_res))
    for i in floor_points:
        x, y = coordinate_to_grid(i[0],i[1], i[2])
        if 0 <= x < grid.shape[0] and 0 <= y < grid.shape[1]: #edited
            grid[x,y]=1



    return grid, bb, voxel_size, coordinate_to_grid ,grid_to_coordinate


def get_z_norm_of_plane(a:float, b:float, c:float, d:float, points: np.ndarray)->np.ndarray:
    """
    Get the normal vector of the plane
    Args:
        a: float
        b: float
        c: float
        d: float
        points: np.ndarray
    Returns:
        np.ndarray: the normal vector of the plane where it points upwards
    """
    norm_z = np.array([a,b,c])
    norm_z = norm_z / np.linalg.norm(norm_z)
    #sample 20 points from the point cloud
    # and align the norm z so that the projected mean of the ten sampled points are positive
    samples = np.random.randint(0,len(points)-1, 20)
    samples = points[samples]
    samples = np.dot(samples, norm_z)
    if np.sum(samples) < 0:
        norm_z = norm_z * (-1.0)
    return norm_z

def rotation_matrix_from_vectors(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2 """

    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]],
                     [v[2], 0, -v[0]],
                     [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

def get_floor_mean(floor_points: np.ndarray)->float:
    return floor_points[:,2].mean()

def astar(floor_grid, start_point, end_point):
    """calculate the shortest path from start_point to end_point using A* algorithm

    Args:
        grid (_type_): a 2D numpy array representing the environment, 1 for obstacle, 0 for free space
        start_point (_type_): _description_
        end_point (_type_): _description_

    Returns:
        _type_: a list of points in the shortest path
    """
    grid = floor_grid==0
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(point):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                x = point[0] + i
                y = point[1] + j
                if x >= 0 and x < grid.shape[0] and y >= 0 and y < grid.shape[1]:
                    neighbors.append((x, y))
        return neighbors

    def get_path(came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(start_point)
        return path[::-1]

    open_set = set([start_point])
    came_from = {}
    g_score = {start_point: 0}
    f_score = {start_point: heuristic(start_point, end_point)}

    while open_set:
        current = min(open_set, key=lambda x: f_score[x])
        if current == end_point:
            return get_path(came_from, current)

        open_set.remove(current)
        for neighbor in get_neighbors(current):
            tentative_g_score = g_score[current] + 1
            if grid[neighbor[0], neighbor[1]] == 0:
                continue
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, end_point)
                if neighbor not in open_set:
                    open_set.add(neighbor)
    #if there is no path: return the start and end point
    return [start_point, end_point]

def get_object_grid_coordinates(coords:np.ndarray, coord_to_grid:callable)->np.ndarray:
    """
    Get the grid coordinates of the object
    Args:
        coords: np.ndarray: the 3d coordinates of the object (N,3)
        coord_to_grid: callable: (x,y,z)->(x,y) a function that converts the 3d coordinates to grid coordinates
        grid: np.ndarray

    Returns:
        np.ndarray: the grid coordinates of the object
    """
    grid_coords = []
    for i in coords:
        x, y = coord_to_grid(i[0],i[1], i[2])
        grid_coords.append((x,y))
    return np.array(grid_coords)

def get_starting_point(grid_coords:np.ndarray, grid:np.ndarray)->(int,int):
    """
    Get the starting point of the path planning that is not an obstacle
    Args:
        grid_coords: np.ndarray: the grid coordinates of the object
        grid: np.ndarray: the floor grid

    Returns:
        (int,int): the starting point of the path planning
    """

    coords_center = grid_coords.mean(axis=0)
    coords_center = (int(coords_center[0]), int(coords_center[1]))
    #get the coordinate of the opposing corner
    #the coordinate of the four corners of the grid
    corners = [(0,0),(0,grid.shape[1]),(grid.shape[0],0),(grid.shape[0],grid.shape[1])]
    #get the corner that is fartherst to the center of the object
    corner = max(corners, key=lambda x: np.linalg.norm(np.array(x)-np.array(coords_center)))
    #get the first grid cell between the center of the grid and the center of the object that is not an obstacle

    #get all the grid cells between the center of the grid and the center of the object
    if corner[0] > coords_center[0]:
        region_x = np.arange(coords_center[0], corner[0])
    else:
        region_x = np.arange(coords_center[0], corner[0], -1)
    if corner[1] > coords_center[1]:
        region_y = np.arange(coords_center[1], corner[1])
    else:
        region_y = np.arange(coords_center[1], corner[1], -1)
    #get the cell closest to the obstacle of the grid that is not an obstacle
    distance = np.inf
    res = None
    for i in region_x:
        for j in region_y:
# end_point = get_starting_point(target_pos_instance_grid_coords, grid)
#   File "/mnt/c/Users/Marc/Desktop/dev/ORganizAR_MAR_DEMO/viewer/path_planning/path_planning.py", line 218, in get_starting_point
#     if grid[i,j] == 0:
# IndexError: index 130 is out of bounds for axis 0 with size 100
            if 0 <= i < grid.shape[0] and 0 <= j < grid.shape[1]: #edited
                if grid[i,j] == 0:
                    d = np.linalg.norm(np.array([i,j])-np.array(coords_center))
                    if d < distance:
                        distance = d
                        res = (i,j)
    return res

def is_in_hull(x:int, y:int, points:list, original_area: float)->bool:
    """
    Check if the point is in the convex hull
    Args:
        p: np.ndarray: the point
        hull: ConvexHull: the convex hull

    Returns:
        bool: True if the point is in the convex hull formed by the points
    """

    #get the area of the convex hull with the point
    points.append((x,y))
    points_np = np.array(points)
    hull_area_with_point = ConvexHull(points).area

    res =not (hull_area_with_point > original_area)

    points.pop()
    #if the area of the convex hull with the point is greater than the original area, then the point is in the convex hull
    return res

def register_moved_target(bb3d: np.ndarray, floor_plan: np.ndarray, coord_to_grid: callable, original_position: np.ndarray)->np.ndarray:
    """
    Register the moved target in the floor plan and free up space in original position
    Args:
        bb: np.ndarray: the bounding box of the floor plan
        floor_plan: np.ndarray: the floor plan
        coord_to_grid: callable: the function that converts the 3d coordinates to grid coordinates
        original_position: np.ndarray: the original position of the target (X,Y)

    Returns:
        np.ndarray: the updated floor plan
    """
    bb3d_grid = []
    for i in bb3d:
        x, y = coord_to_grid(i[0], i[1], i[2])
        bb3d_grid.append((x, y))
    bb3d_grid_np = np.array(bb3d_grid)
    #get the area of the convex hull
    max_x = bb3d_grid_np[:,0].max()
    min_x = bb3d_grid_np[:,0].min()
    max_y = bb3d_grid_np[:,1].max()
    min_y = bb3d_grid_np[:,1].min()
    x_range= np.arange(min_x, max_x)
    y_range = np.arange(min_y, max_y)
    hull_area = ConvexHull(bb3d_grid_np).area
    print("original hull area: ", hull_area)
    print(x_range)
    print(y_range)
    #iterate through the possible grid points and then check if the point is in the convex hull
    for x in x_range:
        for y in y_range:
            if 0 <= x < floor_plan.shape[0] and 0 <= y < floor_plan.shape[1]: #edited
                if floor_plan[x,y] == 0:

                    #check if the point is in the convex hull
                    if is_in_hull(x,y, bb3d_grid, hull_area):
                        #if the point is in the convex hull, then the point is occupied

                        floor_plan[x,y] = 1
                    else:
                        continue

    radius = np.linalg.norm((max_x-min_x,max_y-min_y))/2
    #free up space in the original position
    for x in range(0,floor_plan.shape[0]):
        for y in range(0,floor_plan.shape[1]):
            if 0 <= x < floor_plan.shape[0] and 0 <= y < floor_plan.shape[1]: #edited
                if np.linalg.norm(np.array([x,y])-np.array(original_position)) < radius and floor_plan[x,y] == 1:
                    floor_plan[x,y] = 0

    return floor_plan



class ObjectManager:
    def __init__(self, seg_mask:dict, point_cloud:np.ndarray, coord_to_grid:callable):
        self.masks = seg_mask['ins']
        self.classes = [int(i) for i in seg_mask['final_class']]
        self.points = point_cloud
        self.coor_to_grid = coord_to_grid
    def get_obj_coordinate(self, obj_id:int)->np.ndarray:
        """
        Get the coordinate of the object
        Args:
            obj_id:

        Returns:
            returns the center of the object

        """
        if obj_id not in self.classes:
            return None

        #if there is an object with the id
def get_diagonal_line(lowe_left:(int,int), upper_right:(int,int))->list[(int,int)]:
    x1 = lowe_left[0]
    y1 = lowe_left[1]
    x2 = upper_right[0]
    y2 = upper_right[1]
    res = []
    num_steps = max(abs(y2-y1),abs(x2-x1))
    #pdb.set_trace()
    step_size_x: float = (x2-x1)/num_steps
    step_size_y: float = (y2-y1)/num_steps
    current_step_x:float = float(x1)
    current_step_y:float = float(y1)
    for i in range(num_steps):
        res.append((int(current_step_x),int(current_step_y)))
        current_step_x+=step_size_x
        current_step_y+=step_size_y
    return res
    




# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    point_cloud_path = "./path_planning/data/downsampled_pcd.ply"
    seg_masks_path = "./path_planning/data/filtered_3d_masks.pth"
    point_cloud: o3d.geometry.PointCloud = o3d.io.read_point_cloud(point_cloud_path)
    seg_mask = torch.load(seg_masks_path, map_location=torch.device('cuda'))
    #segment out the planes

    plane_model, inliers = point_cloud.segment_plane(distance_threshold=0.1,
                                             ransac_n=3,
                                             num_iterations=1000)




    norm_z = plane_model[0:3]
    #randomly sample 10 points from the point cloud
    # and align the norm z so that the projected mean of the ten sampled points are positive
    samples = np.random.randint(0,len(point_cloud.colors)-1, 10)
    coordinates = np.asarray(point_cloud.points)
    samples = coordinates[samples]
    samples = np.dot(samples,norm_z)
    if np.sum(samples) < 0:
        norm_z = norm_z*(-1.0)

    original_z = [0,0,1]
    assert len(norm_z) == 3
    rotate = rotation_matrix_from_vectors(original_z,norm_z)
    transform_matrix = np.eye(4,dtype=float)
    transform_matrix[0:3,0:3] = rotate
    point_cloud.transform(transform_matrix)

    color_array = np.asarray(point_cloud.colors)
    coordinates = np.asarray(point_cloud.points)
    z_mean = coordinates[inliers][:,2].mean()

    grid, bb, voxel_size, coor_to_grid, grid_to_coor = get_floor_grid(coordinates,z_mean,1000 )



    #color_array[inliers] = [1.0,0.0,0.0]

    # samples = np.random.randint(0, len(inliers) - 1, 60)
    #
    # pdb.set_trace()
    # print(np.asarray(point_cloud.points)[np.array(inliers)[samples]])
    plt.imshow(grid==1)
    plt.show()


    #pdb.set_trace()

    #o3d.visualization.draw(point_cloud)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
