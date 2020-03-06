using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Rotate : MonoBehaviour
{

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        var speed = 30;
        if (Input.GetKey(KeyCode.A))
            transform.Rotate(Vector3.up * speed * Time.deltaTime);

        if (Input.GetKey(KeyCode.D))
            transform.Rotate(-Vector3.up * speed * Time.deltaTime);

        if (Input.GetKey(KeyCode.W))
            transform.Rotate(Vector3.right * speed * Time.deltaTime);

        if (Input.GetKey(KeyCode.S))
            transform.Rotate(-Vector3.right * speed * Time.deltaTime);


    }


}
