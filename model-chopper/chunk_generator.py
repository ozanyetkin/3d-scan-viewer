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
min_x = min([bbox[i][0] for i in range(8)])
max_x = max([bbox[i][0] for i in range(8)])
min_y = min([bbox[i][1] for i in range(8)])
max_y = max([bbox[i][1] for i in range(8)])
min_z = min([bbox[i][2] for i in range(8)])
max_z = max([bbox[i][2] for i in range(8)])

chunk_width = (max_x - min_x) / grid_size[0]
chunk_height = (max_y - min_y) / grid_size[1]

# Function to create a bounding box
def create_bounding_box(min_x, max_x, min_y, max_y, min_z, max_z):
    bpy.ops.mesh.primitive_cube_add(location=((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2))
    cube = bpy.context.active_object
    cube.scale = [(max_x - min_x) / 2, (max_y - min_y) / 2, (max_z - min_z) / 2]
    return cube

# Function to cut the object with the bounding box and export the chunk
def create_and_export_chunk(obj, min_x, max_x, min_y, max_y, chunk_count):
    # Create the bounding box
    bbox_cube = create_bounding_box(min_x, max_x, min_y, max_y, min_z, max_z)
    
    # Add a boolean modifier to the object
    bool_mod = obj.modifiers.new(name=f"Chunk_{chunk_count}", type='BOOLEAN')
    bool_mod.operation = 'INTERSECT'
    bool_mod.object = bbox_cube
    bpy.context.view_layer.objects.active = obj
    
    # Apply the boolean modifier
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    
    # Separate the chunk into a new object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Select the new chunk and export it
    chunk = bpy.context.selected_objects[-1]  # The newly separated chunk
    chunk_name = f"chunk_{chunk_count}"
    chunk_filename = f"{chunk_name}.glb"
    chunk_filepath = os.path.join(output_dir, chunk_filename)
    
    bpy.ops.object.select_all(action='DESELECT')
    chunk.select_set(True)
    bpy.ops.export_scene.gltf(filepath=chunk_filepath, export_format='GLB')
    
    # Delete the bounding box and the chunk object from the scene
    bpy.data.objects.remove(bbox_cube, do_unlink=True)
    bpy.data.objects.remove(chunk, do_unlink=True)

# Loop over the grid and create chunks
chunk_count = 1
for i in range(grid_size[0]):
    for j in range(grid_size[1]):
        min_x_chunk = min_x + i * chunk_width
        max_x_chunk = min_x + (i + 1) * chunk_width
        min_y_chunk = min_y + j * chunk_height
        max_y_chunk = min_y + (j + 1) * chunk_height
        
        create_and_export_chunk(obj, min_x_chunk, max_x_chunk, min_y_chunk, max_y_chunk, chunk_count)
        
        chunk_count += 1

print('Model chunking complete. Chunks saved to:', output_dir)
