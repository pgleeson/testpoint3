 
import pyvista as pv
import sys

from pyneuroml import pynml

filename = sys.argv[1] if len(sys.argv)==2 else 'c302_C1_Full.net.nml'

net = pynml.read_neuroml2_file(filename).networks[0]
print('Loaded NeuroML file: %s'%filename)

pl = pv.Plotter()

for pop in net.populations:
    

    for p in pop.properties:
        if p.tag=='color':
            colour = [float(w) for w in p.value.split()]

    print('Pop: %s - (%s) - %s'%(pop.id, pop.get_size(), colour))
    for inst in pop.instances:
        loc = inst.location
        sphere = pv.Sphere(center=(loc.x, loc.y, loc.z), radius=3)

        pl.add_mesh(sphere, color=colour)

#pl.enable_mesh_picking()
pl.show()