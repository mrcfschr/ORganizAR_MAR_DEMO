using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SelectSetUp : MonoBehaviour
{
    // Public GameObjects to be assigned in the Unity Editor
    public GameObject gameObject1;
    public GameObject gameObject2;
    public GameObject gameObject3;
    public GameObject items;
    public List<GameObject> spheres;
    public RemoteUnitySceneCustom remoteUnitySceneCustom;

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {

    }


    public void ActivateGameObject1()
    {
        
        gameObject1.SetActive(true);
        gameObject2.SetActive(false);
        gameObject3.SetActive(false);
        remoteUnitySceneCustom.SetTargetRenderings(gameObject1);
    }


    public void ActivateGameObject2()
    {
       
        gameObject2.SetActive(true);
        gameObject1.SetActive(false);
        gameObject3.SetActive(false);
        remoteUnitySceneCustom.SetTargetRenderings(gameObject2);
    }

    public void ActivateGameObject3()
    {
        
        gameObject3.SetActive(true);
        gameObject1.SetActive(false);
        gameObject2.SetActive(false);
        remoteUnitySceneCustom.SetTargetRenderings(gameObject3);
    }

    public void DoneSelectingSetUP()
    {
        items.SetActive(false);
        foreach (GameObject item in spheres) {

            item.SetActive(false);
        }

    }

    


}
