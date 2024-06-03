import bpy
import os
import math

def chunk_and_export_object(obj, chunk_size, export_path):
    # Get the dimensions of the object
    dims = obj.dimensions

    # Calculate the number of chunks in each dimension
    chunks_x = math.ceil(dims.x / chunk_size)
    chunks_y = math.ceil(dims.y / chunk_size)
    chunks_z = math.ceil(dims.z / chunk_size)

    # Create a new collection to hold the chunks
    chunk_collection = bpy.data.collections.new(obj.name + "_chunks")
    bpy.context.scene.collection.children.link(chunk_collection)

    # Loop over the dimensions
    for x in range(chunks_x):
        for y in range(chunks_y):
            for z in range(chunks_z):
                # Duplicate the object
                chunk = obj.copy()
                chunk.data = obj.data.copy()
                chunk_collection.objects.link(chunk)

                # Set the location of the chunk
                chunk.location.x += x * chunk_size
                chunk.location.y += y * chunk_size
                chunk.location.z += z * chunk_size

                # Add a boolean modifier to cut the chunk
                mod = chunk.modifiers.new("Chunk", 'BOOLEAN')
                mod.operation = 'INTERSECT'
                mod.object = bpy.data.objects.new("Chunk_cutter", bpy.data.meshes.new("Chunk_cutter"))
                mod.object.dimensions = (chunk_size, chunk_size, chunk_size)
                mod.object.location = chunk.location

                # Apply the modifier
                bpy.ops.object.modifier_apply({"object": chunk}, modifier=mod.name)

    # Ensure the export path exists
    os.makedirs(export_path, exist_ok=True)

    # Loop over all objects in the collection
    for obj in chunk_collection.objects:
        # Select the object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)

        # Set the export path for this object
        file_path = os.path.join(export_path, obj.name + ".glb")

        # Export the object
        bpy.ops.export_scene.gltf(filepath=file_path)

# Get the active object
obj = bpy.context.active_object

# Chunk the object and export the chunks
chunk_and_export_object(obj, 1.0, "./chunks/")