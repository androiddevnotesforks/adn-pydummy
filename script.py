import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Enables 3D plotting (may be implicit in recent matplotlib)
import itertools
from matplotlib.animation import FuncAnimation

# --- Parameters and Setup ---

# The tesseract (4D hypercube) will have boundaries in every coordinate from -1 to 1.
bounds = (-1, 1)

# Ball parameters: a 4D position, a small "radius" (used only for detecting collisions), and a 4D velocity.
ball_radius = 0.1
ball_pos = np.array([0.0, 0.0, 0.0, 0.0])  # initial 4D position
# Start with a random velocity in each coordinate (you can tweak the range for speed)
ball_vel = np.random.uniform(-0.5, 0.5, 4)

# Time step for simulation updates
dt = 0.02

# The parameter d determines the "eye" distance in the perspective projection from 4D to 3D.
# (Choosing d > max(|w|) helps avoid division-by-zero issues.)
projection_distance = 3.0

# --- Projection Function ---

def project_point(point4d, d=projection_distance):
    """
    Projects a 4D point to 3D using a simple perspective projection.
    The projection formula is:
        (x, y, z, w)  --> (x', y', z')
    where factor = d / (d - w), so:
        x' = x * factor, etc.
    """
    x, y, z, w = point4d
    factor = d / (d - w)
    return np.array([x * factor, y * factor, z * factor])

# --- Tesseract (4D Hypercube) Wireframe ---

# Compute all 16 vertices of the tesseract.
vertices_4d = np.array(list(itertools.product([-1, 1], repeat=4)))

# Two vertices are connected by an edge if they differ in exactly one coordinate.
edges = []
n_vertices = vertices_4d.shape[0]
for i in range(n_vertices):
    for j in range(i + 1, n_vertices):
        # Since each coordinate is either -1 or 1, a difference in one coordinate gives an absolute difference of 2.
        if np.sum(np.abs(vertices_4d[i] - vertices_4d[j]) == 2) == 1:
            edges.append((vertices_4d[i], vertices_4d[j]))

# Project the endpoints of each edge to 3D.
projected_edges = []
for edge in edges:
    p1_3d = project_point(edge[0])
    p2_3d = project_point(edge[1])
    projected_edges.append((p1_3d, p2_3d))

# --- Ball Update Function ---

def update_ball():
    """
    Updates the ball’s position based on its velocity and reflects its velocity
    when it hits any of the 4D boundaries.
    """
    global ball_pos, ball_vel
    ball_pos = ball_pos + ball_vel * dt
    # Check each coordinate for collision with the tesseract walls.
    for i in range(4):
        if ball_pos[i] + ball_radius > bounds[1]:
            ball_pos[i] = bounds[1] - ball_radius  # reposition inside
            ball_vel[i] *= -1                      # reflect velocity
        elif ball_pos[i] - ball_radius < bounds[0]:
            ball_pos[i] = bounds[0] + ball_radius
            ball_vel[i] *= -1

# --- Matplotlib Figure Setup ---

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# Set reasonable limits for the 3D projection (you may adjust these if needed).
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_zlim(-2, 2)
ax.set_box_aspect([1, 1, 1])
ax.set_title("Ball Bouncing Inside a Tesseract (4D)")

# Draw the tesseract edges.
for edge in projected_edges:
    xs = [edge[0][0], edge[1][0]]
    ys = [edge[0][1], edge[1][1]]
    zs = [edge[0][2], edge[1][2]]
    ax.plot(xs, ys, zs, color='gray', lw=0.5)

# Initialize the ball’s 3D projected position.
ball_proj = project_point(ball_pos)
ball_scatter = ax.scatter([ball_proj[0]], [ball_proj[1]], [ball_proj[2]], color='red', s=100)

# --- Animation Update Function ---

def update(frame):
    """
    This function is called by FuncAnimation to update the simulation.
    It moves the ball, projects its new 4D position into 3D, and updates the plot.
    """
    update_ball()  # update simulation state
    ball_proj = project_point(ball_pos)
    # The 3D scatter object stores its data in a protected member _offsets3d;
    # updating it is a commonly used (if not officially documented) method.
    ball_scatter._offsets3d = ([ball_proj[0]], [ball_proj[1]], [ball_proj[2]])
    return ball_scatter,

# Create the animation. (frames can be increased for a longer simulation.)
ani = FuncAnimation(fig, update, frames=500, interval=20, blit=False)

plt.show()
