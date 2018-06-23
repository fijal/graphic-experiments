using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TextureHolder : MonoBehaviour {

    public RenderTexture texture;
    public Shader shader;

	// Use this for initialization
	void Start () {
        texture = new RenderTexture(512, 512, 16);
        GetComponent<Camera>().targetTexture = texture;
	}
	
	// Update is called once per frame
	void Update () {
        GetComponent<Camera>().RenderWithShader(shader, "");	
	}
}
