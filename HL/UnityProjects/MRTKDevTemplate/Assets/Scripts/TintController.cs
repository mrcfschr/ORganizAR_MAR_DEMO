using UnityEngine;

public class TintController : MonoBehaviour
{
    public float tintValue; 
    private Renderer modelRenderer;
    public bool switchColor = false;
    public Color startColor = Color.red;
    public Color endColor = Color.green;

    public void Start()
    {
        this.modelRenderer = GetComponent<Renderer>();
    }

    public void ToggleColor() {
        switchColor = !switchColor;
    }
    void Update()
    {
        if (switchColor)
        {
            startColor = Color.blue;
            endColor = Color.yellow;
        }
        else {
            startColor = Color.red;
            endColor = Color.green;

        }
        Color newColor = Color.Lerp(startColor, endColor, tintValue);
        if (modelRenderer != null)
        {
            modelRenderer.material.color = newColor;
        }
    }
}
