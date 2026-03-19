import os
import numpy as np
import trimesh
import pyvista as pv

# 1. Load STL mesh
mesh = trimesh.load_mesh("data/beam.stl")

print("Vertices:", len(mesh.vertices))
print("Faces:", len(mesh.faces))
print("Watertight:", mesh.is_watertight)

if not mesh.is_watertight:
    print("Warning: mesh is not watertight. Point containment may be unreliable.")

# 2. Get mesh bounding box
bounds = mesh.bounds
mins = bounds[0]   # [xmin, ymin, zmin]
maxs = bounds[1]   # [xmax, ymax, zmax]

print("Bounding box min:", mins)
print("Bounding box max:", maxs)

# 3. Generate a 3D grid of candidate points
#    Shift by half spacing so points do not
#    land exactly on the surface
spacing = 0.1
padding = 0.1

x = np.arange(mins[0] - padding + spacing / 2, maxs[0] + padding, spacing)
y = np.arange(mins[1] - padding + spacing / 2, maxs[1] + padding, spacing)
z = np.arange(mins[2] - padding + spacing / 2, maxs[2] + padding, spacing)

X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
points = np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))

print("Total candidate grid points:", len(points))

# 4. Keep only points inside the mesh
inside_mask = mesh.contains(points)
inside_points = points[inside_mask]

print("Points inside shape:", len(inside_points))

# 5. Tag boundary-condition regions
#    0 = interior
#    1 = fixed
#    2 = load
labels = np.zeros(len(inside_points), dtype=int)

tol = spacing * 0.6

# Tag based on actual mesh bounds, not particle min/max
labels[inside_points[:, 0] <= mins[0] + tol] = 1
labels[inside_points[:, 0] >= maxs[0] - tol] = 2

fixed_count = np.sum(labels == 1)
load_count = np.sum(labels == 2)
interior_count = np.sum(labels == 0)

print("Interior points:", interior_count)
print("Fixed points:", fixed_count)
print("Load points:", load_count)

# 6. Convert trimesh mesh to PyVista mesh
faces = mesh.faces
vertices = mesh.vertices

pv_faces = []
for face in faces:
    pv_faces.extend([3, face[0], face[1], face[2]])

pv_mesh = pv.PolyData(vertices, pv_faces)

# 7. Create point cloud for visualization
point_cloud = pv.PolyData(inside_points)
point_cloud["label"] = labels

# 8. Export particle data
os.makedirs("outputs", exist_ok=True)

particle_data = np.column_stack((inside_points, labels))
np.savetxt(
    "outputs/beam_particles.csv",
    particle_data,
    delimiter=",",
    header="x,y,z,label",
    comments=""
)
print("Saved outputs/beam_particles.csv")

point_cloud.save("outputs/beam_particles.vtp")
print("Saved outputs/beam_particles.vtp")

# 9. Plot mesh + labeled particles
plotter = pv.Plotter()
plotter.add_mesh(pv_mesh, show_edges=True, opacity=0.25)
plotter.add_points(
    point_cloud,
    scalars="label",
    point_size=12,
    render_points_as_spheres=True
)
plotter.add_axes()
plotter.show()