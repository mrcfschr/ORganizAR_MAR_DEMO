using UnityEngine;

public class GetBottomBounds : MonoBehaviour
{
    // Function to get a specific bottom corner based on the index passed
    public Vector3 GetBottomCorner(int index)
    {
        if (index < 0 || index > 3)
        {
            Debug.LogError("Index out of range. Valid indices are 0 to 3.");
            return Vector3.zero;
        }

        MeshFilter meshFilter = GetComponent<MeshFilter>();
        if (meshFilter == null)
        {
            Debug.LogError("MeshFilter not found!");
            return Vector3.zero;
        }

        // Get the mesh bounds in local space
        Bounds bounds = meshFilter.mesh.bounds;

        // Get the 4 bottom corners of the bounding box
        Vector3[] corners = new Vector3[4];

        // Calculate the corners in local space
        Vector3 center = bounds.center;
        Vector3 extents = bounds.extents;

        corners[0] = center + new Vector3(-extents.x, -extents.y, -extents.z);
        corners[1] = center + new Vector3(extents.x, -extents.y, -extents.z);
        corners[2] = center + new Vector3(-extents.x, -extents.y, extents.z);
        corners[3] = center + new Vector3(extents.x, -extents.y, extents.z);

        // Transform the specified corner to world space
        return transform.TransformPoint(corners[index]);
    }
}
