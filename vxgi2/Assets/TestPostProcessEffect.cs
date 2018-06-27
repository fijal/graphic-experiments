using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class TestPostProcessEffect : MonoBehaviour
{
    /* Set as a component in the main camera. */

    public Shader shader;

    Texture3D rend3d;
    Material mat;

    private void Start()
    {
        rend3d = new Texture3D(64, 64, 64, TextureFormat.Alpha8, mipmap: false);
        rend3d.filterMode = FilterMode.Trilinear;
        rend3d.wrapMode = TextureWrapMode.Repeat;

        Color32[] colors = new Color32[64 * 64 * 64];
        int i = 0;
        for (int z = 0; z < 64; z++)
            for (int y = 0; y < 64; y++)
                for (int x = 0; x < 64; x++)
                {
                    float f = 0;

                    Vector3 v = new Vector3(x - 32.5f, z - 32, Mathf.Min(y, 64 - y));
                    f += 20f / v.sqrMagnitude;

                    /*if ((x & 1) == 0)
                        f = 0;
                    else
                        f = 0.5f;*/

                    int r = (int)(f * 256f);
                    if (r > 255) r = 255;

                    colors[i++] = new Color32(0, 0, 0, (byte)r);
                }
        Debug.Assert(i == colors.Length);
        rend3d.SetPixels32(colors);
        rend3d.Apply();

        GetComponent<Camera>().depthTextureMode = DepthTextureMode.Depth;

        mat = new Material(shader);
    }

    private void OnRenderImage(RenderTexture source, RenderTexture destination)
    {
        var camera = GetComponent<Camera>();
        mat.SetMatrix("_ViewProjectInverse", (camera.projectionMatrix * camera.worldToCameraMatrix).inverse);

        mat.SetTexture("_Rend3D", rend3d);

        Graphics.Blit(source, destination, mat);
    }
}
