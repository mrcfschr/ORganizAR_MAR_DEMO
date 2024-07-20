using UnityEngine;

[RequireComponent(typeof(MeshRenderer))]
[RequireComponent(typeof(MeshFilter))]
[RequireComponent(typeof(Collider))]
public class ToggleMeshRenderer : MonoBehaviour
{
    private MeshRenderer meshRenderer;
    private Collider objectCollider;
    private Camera mainCamera;

    void Start()
    {
        meshRenderer = GetComponent<MeshRenderer>();
        objectCollider = GetComponent<Collider>();
        mainCamera = Camera.main;

        if (mainCamera == null)
        {
            Debug.LogError("Main camera not found!");
            enabled = false;
        }
    }

    void Update()
    {
        if (IsCameraInsideBounds())
        {
            if (meshRenderer.enabled)
            {
                meshRenderer.enabled = false;
            }
        }
        else
        {
            if (!meshRenderer.enabled)
            {
                meshRenderer.enabled = true;
            }
        }
    }

    private bool IsCameraInsideBounds()
    {
        if (objectCollider == null || mainCamera == null) return false;

        return objectCollider.bounds.Contains(mainCamera.transform.position);
    }
}
