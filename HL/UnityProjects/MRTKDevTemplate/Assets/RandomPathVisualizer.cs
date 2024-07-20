using UnityEngine;
using System.Collections.Generic;

public class RandomPathVisualizer : MonoBehaviour
{
    public string pathVizPrefabPath = "pathViz"; // Path to the prefab in the Resources folder
    public int controlPointCount = 10; // Number of control points
    public int smoothness = 10; // Number of points between each pair of control points

    void Start()
    {
        // Load the prefab from the Resources folder
        GameObject pathVizPrefab = Resources.Load<GameObject>(pathVizPrefabPath);

        if (pathVizPrefab == null)
        {
            Debug.LogError("Prefab not found at path: " + pathVizPrefabPath);
            return;
        }

        // Instantiate the prefab
        GameObject pathVizInstance = Instantiate(pathVizPrefab);
        pathVizInstance.transform.SetParent(transform);

        // Get the LineRenderer component
        LineRenderer lineRenderer = pathVizInstance.GetComponent<LineRenderer>();

        if (lineRenderer == null)
        {
            Debug.LogError("LineRenderer component not found on the prefab.");
            return;
        }

        // Generate random control points
        Vector3[] controlPoints = new Vector3[controlPointCount];
        for (int i = 0; i < controlPointCount; i++)
        {
            float x = Random.Range(-5.0f, 5.0f);
            float z = Random.Range(-5.0f, 5.0f);
            controlPoints[i] = new Vector3(x, 0, z);
        }

        // Generate smooth path points using Catmull-Rom spline
        List<Vector3> pathPoints = new List<Vector3>();
        for (int i = 0; i < controlPoints.Length - 1; i++)
        {
            Vector3 p0 = controlPoints[Mathf.Max(i - 1, 0)];
            Vector3 p1 = controlPoints[i];
            Vector3 p2 = controlPoints[Mathf.Min(i + 1, controlPoints.Length - 1)];
            Vector3 p3 = controlPoints[Mathf.Min(i + 2, controlPoints.Length - 1)];

            for (int j = 0; j < smoothness; j++)
            {
                float t = j / (float)smoothness;
                Vector3 point = CatmullRom(p0, p1, p2, p3, t);
                pathPoints.Add(point);
            }
        }

        // Add the last control point
        pathPoints.Add(controlPoints[controlPoints.Length - 1]);

        // Set the points to the LineRenderer
        lineRenderer.positionCount = pathPoints.Count;
        lineRenderer.SetPositions(pathPoints.ToArray());
    }

    Vector3 CatmullRom(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
    {
        // Catmull-Rom spline formula
        return 0.5f * (
            2f * p1 +
            (-p0 + p2) * t +
            (2f * p0 - 5f * p1 + 4f * p2 - p3) * t * t +
            (-p0 + 3f * p1 - 3f * p2 + p3) * t * t * t
        );
    }
}
