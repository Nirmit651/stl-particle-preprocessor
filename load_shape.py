import trimesh
import pyvista as pv

# Create a simple box directly in code
mesh = trimesh.creation.box(extents=(1, 1, 1))

# Print basic information
print("Vertices:", len(mesh.vertices))
print("Faces:", len(mesh.faces))
print("Watertight:", mesh.is_watertight)
print("Bounds:")
print(mesh.bounds)

# Convert trimesh mesh to PyVista mesh for visualization
faces = mesh.faces
vertices = mesh.vertices

# PyVista expects faces in a flattened format:
# [3, v1, v2, v3, 3, v1, v2, v3, ...]
pv_faces = []
for face in faces:
    pv_faces.extend([3, face[0], face[1], face[2]])

pv_mesh = pv.PolyData(vertices, pv_faces)

plotter = pv.Plotter()
plotter.add_mesh(pv_mesh, show_edges=True, opacity=0.6)
plotter.add_axes()
plotter.show()