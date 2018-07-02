using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class ImageEffect2 : MonoBehaviour
{
    public Shader imageEffect2Shader;
    public Transform vlightPrefab;
    public Texture3D rend3d;

    Material mat;

    const int RESOLUTION = 32;
    const float INV_SCALE = 32f;

    private void Start()
    {
        rend3d = new Texture3D(RESOLUTION, RESOLUTION, RESOLUTION, TextureFormat.Alpha8, mipmap: false);
        rend3d.filterMode = FilterMode.Trilinear;
        rend3d.wrapMode = TextureWrapMode.Clamp;

        Color32[] colors = new Color32[rend3d.width * rend3d.height * rend3d.depth];

        for (int i = 0; i < 10; i++)
        {
            int tx = Random.Range(1, rend3d.width - 1);
            int ty = Random.Range(1, rend3d.height / 2 - 1);
            int tz = Random.Range(1, rend3d.depth - 1);
            colors[tx + rend3d.width * (ty + rend3d.height * tz)] = new Color32(0, 0, 0, 255);

            Transform tr = Instantiate(vlightPrefab);
            tr.position = new Vector3(tx + 0.5f, ty + 0.5f, tz + 0.5f) / INV_SCALE;
        }
        rend3d.SetPixels32(colors);
        rend3d.Apply();// updateMipmaps: true);

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

    private void OnRenderImage(RenderTexture source, RenderTexture destination)
    {
        var camera = GetComponent<Camera>();
        mat.SetMatrix("_ViewProjectInverse", (camera.projectionMatrix * camera.worldToCameraMatrix).inverse);
        mat.SetTexture("_Rend3D", rend3d);
        Graphics.Blit(source, destination, mat);
    }
}
