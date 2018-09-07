using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class ImageEffect2 : MonoBehaviour
{
    public Shader imageEffect2Shader;
    public Transform vlightPrefab;
    public Texture2DArray rend3d;

    Material mat;

    const int RESOLUTION = 32;
    const float INV_SCALE = 32f;
    Color32[][] colors;

    private void Start()
    {
        rend3d = new Texture2DArray(RESOLUTION, RESOLUTION, RESOLUTION, TextureFormat.RGBA32, mipmap: false);
        rend3d.filterMode = FilterMode.Bilinear;
        rend3d.wrapMode = TextureWrapMode.Clamp;

        colors = new Color32[rend3d.depth][];
        for (int k = 0; k < rend3d.depth; k++)
            colors[k] = new Color32[rend3d.width * rend3d.height];

        for (int i = 0; i < 10; i++)
        {
            int tx = UnityEngine.Random.Range(1, rend3d.width - 1);
            int ty = UnityEngine.Random.Range(1, rend3d.height / 2 - 1);
            int tz = UnityEngine.Random.Range(1, rend3d.depth - 1);
            AddColor(tx, ty, tz, new Color(1, 1, 0, 1));

            Transform tr = Instantiate(vlightPrefab);
            tr.position = new Vector3(tx + 0.5f, ty + 0.5f, tz + 0.5f) / INV_SCALE;
        }
        for (int k = 0; k < rend3d.depth; k++)
            rend3d.SetPixels32(colors[k], k);
        rend3d.Apply();

        GetComponent<Camera>().depthTextureMode = DepthTextureMode.Depth;

        mat = new Material(imageEffect2Shader);

#if false
        for (int i = 0; i < 1000; i++)
        {
            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.transform.localScale = new Vector3(0.02f, 0.02f, 0.02f);
            go.transform.localPosition = Random.insideUnitSphere * 1 + new Vector3(0.5f, 0.5f, 0.5f);
        }
#endif
    }

    void AddColor(int tx, int ty, int tz, Color col)
    {
        int delta = 0;

        for (int ty1 = ty; ty1 < rend3d.depth; ty1++)
        {
            var col1 = col / (delta+1);// ((delta * 2 + 1) * (delta * 2 + 1));

            int txmin = Math.Max(tx - delta, 0);
            int txmax = Math.Min(tx + delta, rend3d.width - 1);
            int tzmin = Math.Max(tz - delta, 0);
            int tzmax = Math.Min(tz + delta, rend3d.height - 1);

            for (int tx1 = txmin; tx1 <= txmax; tx1++)
                for (int tz1 = tzmin; tz1 <= tzmax; tz1++)
                    colors[ty1][tx1 + rend3d.width * tz1] += col1;

            delta++;
        }
    }

    private void OnRenderImage(RenderTexture source, RenderTexture destination)
    {
        var camera = GetComponent<Camera>();
        mat.SetMatrix("_ViewProjectInverse", (camera.projectionMatrix * camera.worldToCameraMatrix).inverse);
        mat.SetTexture("_Rend3D", rend3d);
        Graphics.Blit(source, destination, mat);
    }
}
