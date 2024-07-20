using UnityEngine;
using System.Collections.Generic;

public class PointCloudRendererTest : MonoBehaviour
{
    public int maxChunkSize = 65535;
    public float pointSize = 0.005f;
    public GameObject pointCloudElem;
    public Material pointCloudMaterial;

    List<GameObject> elems = new List<GameObject>();

    void Start()
    {
        Init();
        RenderRandomPoints();
    }

    public void Init()
    {
        elems = new List<GameObject>();
        UpdatePointSize();
    }

    void Update()
    {
        if (transform.hasChanged)
        {
            UpdatePointSize();
            transform.hasChanged = false;
        }
    }

    public void UpdatePointSize()
    {
        pointCloudMaterial.SetFloat("_PointSize", pointSize * transform.localScale.x);
    }

    public void Render(Vector3[] arrVertices, Color pointColor)
    {
        int nPoints, nChunks;
        if (arrVertices == null)
        {
            nPoints = 0;
            nChunks = 0;
        }
        else
        {
            nPoints = arrVertices.Length;
            nChunks = 1 + nPoints / maxChunkSize;
        }

        if (elems.Count < nChunks)
            AddElems(nChunks - elems.Count);
        if (elems.Count > nChunks)
            RemoveElems(elems.Count - nChunks);

        int offset = 0;
        for (int i = 0; i < nChunks; i++)
        {
            int nPointsToRender = System.Math.Min(maxChunkSize, nPoints - offset);

            ElemRenderer renderer = elems[i].GetComponent<ElemRenderer>();
            renderer.UpdateMesh(arrVertices, nPointsToRender, offset, pointColor);

            offset += nPointsToRender;
        }
    }

    void AddElems(int nElems)
    {
        for (int i = 0; i < nElems; i++)
        {
            GameObject newElem = GameObject.Instantiate(pointCloudElem);
            newElem.transform.parent = transform;
            newElem.transform.localPosition = new Vector3(0.0f, 0.0f, 0.0f);
            newElem.transform.localRotation = Quaternion.identity;
            newElem.transform.localScale = new Vector3(1.0f, 1.0f, 1.0f);

            elems.Add(newElem);
        }
    }

    void RemoveElems(int nElems)
    {
        for (int i = 0; i < nElems; i++)
        {
            Destroy(elems[0]);
            elems.RemoveAt(0);
        }
    }

    void RenderRandomPoints()
    {
        int numPoints = 100000;
        Vector3[] points = new Vector3[numPoints];
        Color pointColor = Color.white;

        for (int i = 0; i < numPoints; i++)
        {
            points[i] = new Vector3(
                Random.Range(-0.5f, 0.5f),
                Random.Range(-0.5f, 0.5f),
                Random.Range(-0.5f, 0.5f)
            );
        }

        Render(points, pointColor);
    }
}
