import pyvista as pv


pl = pv.Plotter()  

#mesh = pv.read('ImageToStl.com_virtual_worm_neuron_only_march_2011.obj')
#mesh = pv.read('Virtual_Worm_February_2012.obj')
mesh = pv.read('w1.obj')
#pl.add_mesh(mesh, smooth_shading=True)
print(mesh)
print(mesh.faces[:44])
conn = mesh.connectivity('all')
print(conn)
# Format scalar bar text for integer values.
scalar_bar_args = dict(
    fmt='%.f',
)

cpos = [(10.5, 12.2, 18.3), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]

conn.plot(
    categories=True,
    cmap='jet',
    scalar_bar_args=scalar_bar_args,
    cpos=cpos,
)

