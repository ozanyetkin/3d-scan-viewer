import bpy
import os

# Define the directory to save the chunks
output_dir = os.path.join(os.path.expanduser('~'), '3d_model_chunks')

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Define the grid size for chunking (e.g., 2x2 grid)
grid_size = (2, 2)

# Get the current object (ensure your model is selected)
obj = bpy.context.active_object

# Apply any transformations to the object (important for accurate chunking)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Get the bounding box dimensions
bbox = obj.bound_box

# Calculate the chunk size
min_x = min([bbox[i][0] for i in range(8)])
max_x = max([bbox[i][0] for i in range(8)])
min_y = min([bbox[i][1] for i in range(8)])
max_y = max([bbox[i][1] for i in range(8)])
min_z = min([bbox[i][2] for i in range(8)])
max_z = max([bbox[i][2] for i in range(8)])

chunk_width = (max_x - min_x) / grid_size[0]
chunk_height = (max_y - min_y) / grid_size[1]

# Function to create a chunk
def create_chunk(obj, min_x, max_x, min_y, max_y):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    
    # Duplicate the object
    bpy.ops.object.duplicate(linked=False)
    chunk_obj = bpy.context.selected_objects[0]
    
    # Create a new boolean modifier to cut the chunk
    bool_mod = chunk_obj.modifiers.new(name='Chunk', type='BOOLEAN')
    bool_mod.operation = 'INTERSECT'
    
    # Create a cube to use as the boolean object
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
                                    location=((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2))
    cube = bpy.context.active_object
    cube.scale[0] = (max_x - min_x) / 2
    cube.scale[1] = (max_y - min_y) / 2
    cube.scale[2] = (max_z - min_z) / 2
    
    # Set the boolean object
    bool_mod.object = cube
    
    # Apply the boolean modifier
    bpy.context.view_layer.objects.active = chunk_obj
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    
    # Delete the boolean object
    bpy.data.objects.remove(cube, do_unlink=True)
    
    return chunk_obj

# Loop over the grid and create chunks
chunk_count = 1
for i in range(grid_size[0]):
    for j in range(grid_size[1]):
        min_x_chunk = min_x + i * chunk_width
        max_x_chunk = min_x + (i + 1) * chunk_width
        min_y_chunk = min_y + j * chunk_height
        max_y_chunk = min_y + (j + 1) * chunk_height
        
        chunk_obj = create_chunk(obj, min_x_chunk, max_x_chunk, min_y_chunk, max_y_chunk)
        
        # Export the chunk
        chunk_filename = f'chunk_{chunk_count}.glb'
        chunk_filepath = os.path.join(output_dir, chunk_filename)
        bpy.ops.object.select_all(action='DESELECT')
        chunk_obj.select_set(True)
        bpy.ops.export_scene.gltf(filepath=chunk_filepath, export_format='GLB')
        
        # Delete the chunk object
        bpy.data.objects.remove(chunk_obj, do_unlink=True)
        
        chunk_count += 1

print('Model chunking complete. Chunks saved to:', output_dir)
