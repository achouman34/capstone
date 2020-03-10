using System.Collections;
using System.Collections.Generic;
using UnityEngine;



public class Transition: MonoBehaviour
{
    static bool flag = true;
    static int frameCount = 0;
    public GameObject[] objects;
    // Start is called before the first frame update
    void Start()
    {
        foreach (GameObject go in objects)
        {
            go.SetActive(false);
        }
        objects[0].SetActive(true);
    }

    // Update is called once per frame
    void Update()
    {
        frameCount += 1;
        frameCount %= 60;
        if(frameCount == 0)
        {
            for(int i = 0; i < objects.Length; i++)
            {
                if (objects[i].activeSelf)
                {
                    objects[i].SetActive(false);
                    if (i == objects.Length - 1)
                    {
                        objects[0].SetActive(true);
                        break;
                    }
                    else
                    {
                        objects[i + 1].SetActive(true);
                        break;
                    }
                }
            }
        }

        foreach(GameObject go in objects)
        {
            var speed = 30;
            if (Input.GetKey(KeyCode.A))
                go.transform.Rotate(Vector3.up * speed * Time.deltaTime);

            if (Input.GetKey(KeyCode.D))
                go.transform.Rotate(-Vector3.up * speed * Time.deltaTime);

            if (Input.GetKey(KeyCode.W))
                go.transform.Rotate(Vector3.right * speed * Time.deltaTime);

            if (Input.GetKey(KeyCode.S))
                go.transform.Rotate(-Vector3.right * speed * Time.deltaTime);
        }
        

    }

    void OnGUI()
    {
        
    }
}