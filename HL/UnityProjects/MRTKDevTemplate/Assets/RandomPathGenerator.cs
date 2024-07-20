using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RandomPathGenerator : MonoBehaviour
{
    public int numberOfPoints = 10;
    public float width = 0.1f; // 10 cm wide
    public Color pathColor = Color.green;

    private LineRenderer lineRenderer;

    void Start()
    {
        // Initialize LineRenderer
        lineRenderer = gameObject.AddComponent<LineRenderer>();
        lineRenderer.widthMultiplier = width;

        // Create a new material with the Graphics Tools/Standard shader and set it to unlit
        Material lineMaterial = new Material(Shader.Find("Graphics Tools/Standard"));
        lineMaterial.SetColor("_Color", pathColor);
        lineMaterial.SetFloat("_LightingMode", 0); // Set to Unlit mode
        lineRenderer.material = lineMaterial;

        lineRenderer.positionCount = numberOfPoints;

        // Generate random points and set them in the LineRenderer
        Vector3[] points = GenerateRandomPoints();
        lineRenderer.SetPositions(points);
    }

    Vector3[] GenerateRandomPoints()
    {
        Vector3[] points = new Vector3[numberOfPoints];
        for (int i = 0; i < numberOfPoints; i++)
        {
            float x = Random.Range(-3f, 3f); // 6 meters wide space
            float z = Random.Range(-2f, 2f); // 4 meters deep space
            points[i] = new Vector3(x, 0, z);
        }
        return points;
    }

    public void SetColor(Color newColor)
    {
        if (lineRenderer != null)
        {
            lineRenderer.startColor = newColor;
            lineRenderer.endColor = newColor;
            lineRenderer.material.SetColor("_Color", newColor);
        }
    }
}
