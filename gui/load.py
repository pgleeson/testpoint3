import pyvista as pv

import sys
import numpy as np

import time


import sys

from pyneuroml import pynml
from pyneuroml.utils import extract_position_info
from neuroml import Cell


pl = pv.Plotter()

filename = sys.argv[1] if len(sys.argv) == 2 else "c302_D_Full.net.nml"

nml_doc = pynml.read_neuroml2_file(filename, include_includes=True)

print("Loaded NeuroML file: %s" % filename)


(
    cell_id_vs_cell,
    pop_id_vs_cell,
    positions,
    pop_id_vs_color,
    pop_id_vs_radii,
) = extract_position_info(nml_doc, False)

factor = 0.2

while pop_id_vs_cell:
    pop_id, cell = pop_id_vs_cell.popitem()
    pos_pop = positions[pop_id]  # type: typing.Dict[typing.Any, typing.List[float]]

    print("Pop: %s has %i of component %s" % (pop_id, len(pos_pop), cell.id))

    radius = pop_id_vs_radii[pop_id] if pop_id in pop_id_vs_radii else 10
    color = pop_id_vs_color[pop_id] if pop_id in pop_id_vs_color else "r"

    if type(cell) == Cell:
        print("Loading a cell with %i segments" % len(cell.morphology.segments))

        cell_meshes = pv.MultiBlock()

        for seg in cell.morphology.segments:
            p = cell.get_actual_proximal(seg.id)
            d = seg.distal
            width = (p.diameter + d.diameter) / 4
            #print("Creating %s" % (seg))

            if cell.get_segment_length(seg.id) == 0:

                seg_mesh = pv.Sphere(center=(p.x*factor, p.z*factor, -1*p.y*factor), radius=p.diameter*factor / 2)

                # pl.add_mesh(seg_mesh, color=color)
            else:
                seg_mesh = pv.Tube(
                    pointa=(p.x*factor, p.z*factor, -1*p.y*factor),
                    pointb=(d.x*factor, d.z*factor, -1*d.y*factor),
                    resolution=1,
                    radius=width*factor,
                    n_sides=15,
                )

            cell_meshes.append(seg_mesh)

        while pos_pop:
            cell_index, pos = pos_pop.popitem()
            pp=[pos[0]*factor,pos[2]*factor,-1*pos[1]*factor]
            print("Plotting %s(%i) at %s, %s" % (cell.id, cell_index, pos, pp))
            cell_mesh = cell_meshes.copy()
            for i in range(len(cell_mesh)):
                cell_mesh[i].translate(pp, inplace=True)
            pl.add_mesh(cell_mesh, color=color, smooth_shading=True)

    else:
        sphere = pv.Sphere(center=(pos[0], pos[1], pos[2]), radius=radius)

        pl.add_mesh(sphere, color=color)




points = []

types = []

file = "pressure_buffer.txt"
file = "position_buffer.txt"
if len(sys.argv) == 2:
    file = sys.argv[1]

colours = {1.1: "lightblue", 2.1: "green", 2.2: "turquoise", 3: "#eeeeee"}
colours = {1.1: "blue", 2.2: "turquoise"}

line_count = 0
pcount = 0

all_points = []
all_point_types = []

time_count = 0

logStep = None

include_boundary = False

for l in open(file):
    ws = l.split()
    #print(ws)
    if line_count == 6:
        numOfElasticP = int(ws[0])
    if line_count == 7:
        numOfLiquidP = int(ws[0])
    if line_count == 8:
        numOfBoundaryP = int(ws[0])
    if line_count == 9:
        timeStep = float(ws[0])
    if line_count == 10:
        logStep = int(ws[0])

    if len(ws) == 4:
        type = float(ws[3])

        if not (type == 3 and not include_boundary):
            points.append([float(ws[0]), float(ws[1]), float(ws[2])])
            types.append(type)

    if logStep is not None: 
        pcount+=1
        
        if pcount==numOfBoundaryP+numOfElasticP+numOfLiquidP:
            print('End of one batch of %i added, %i total points at line %i, time: %i'%(len(points),pcount, line_count, time_count))
            all_points.append(points)
            all_point_types.append(types)

            points = []
            types=[]
            pcount = 0
            numOfBoundaryP=0

            time_count+=1

        
    line_count += 1

#all_points_np = np.array(all_points)

print(f"Loaded positions with %i elastic, %i liquid and %i boundary points (%i total), %i lines"%(numOfElasticP,numOfLiquidP, numOfBoundaryP,numOfElasticP+numOfLiquidP+numOfBoundaryP, line_count))

print("Num of time points found: %i"%len(all_points))

pl.set_background("lightgrey")

last_mesh = None


def create_mesh(step):
    step_count = step
    value=step_count
    global last_mesh
    index = int(value)

        
    print('Changing to time point: %s (%s) '%(index,value))
    curr_points = all_points[index]
    curr_types = all_point_types[index]
    if last_mesh is None:

        last_mesh = pv.PolyData(curr_points)
        last_mesh["types"] = curr_types
        last_mesh.translate((0,-1000,0), inplace=True)
        print(last_mesh)

        last_actor = pl.add_mesh(
            last_mesh,
            render_points_as_spheres=True,
            cmap=[c for c in colours.values()],
            point_size=3,
        )
    else:
        last_mesh.points = curr_points
        last_mesh.translate((0,-00,-100), inplace=True)

    pl.render()

    time.sleep(0.1)
    
    return
    
create_mesh(0)

max_time = len(all_points)-1
pl.add_slider_widget(create_mesh, rng=[0,max_time], value=max_time, title='Time point')
pl.add_timer_event(   max_steps=5, duration=2, callback=create_mesh)


mesh = pv.read('bwm.obj')
mesh.scale(20, inplace=True)
mesh.translate((-40,0,0), inplace=True)

pl.add_mesh(mesh, smooth_shading=True, color='green')

mesh2 = pv.read('neurons.obj')
mesh2.scale(20, inplace=True)
mesh2.translate((-80,0,0), inplace=True)

pl.add_mesh(mesh2, smooth_shading=True, color='orange')


pl.add_axes()


pl.show()

