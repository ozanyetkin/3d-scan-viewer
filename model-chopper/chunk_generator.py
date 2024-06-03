import bpy
import math

def chunk_object(obj, chunk_size):
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

# Get the active object
obj = bpy.context.active_object

# Chunk the object
chunk_object(obj, 1.0)