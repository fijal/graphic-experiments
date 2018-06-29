using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class OcTreeBuilder : MonoBehaviour
{
    public Transform scene;
    public TestPostProcessEffect postProcessEffect;


    /* octree format: an array of int
     * (some of which could be cast to floats with asfloat() in the shader)
     * 
     * "Node" structure:
     *
     *     mean_color as RGB
     *     8 * substructure_index
     *
     * Each "substructure_index" is an integer:
     * 
     *     0     empty
     *     > 0   another node, at the given index in the octree buffer
     *     < 0   leaf, color = RGB = index & 0xFFFFFF
     */

    ComputeBuffer gpu_octree;
    List<int> cpu_octree;
    

    private void Start()
    {
        BuildCpuOcTree();
        gpu_octree = new ComputeBuffer(cpu_octree.Count, sizeof(int));
        gpu_octree.SetData(cpu_octree);

        var mat = postProcessEffect.GetMaterial();
        mat.SetBuffer("g_OcTree", gpu_octree);
    }

    void BuildCpuOcTree()
    {
        cpu_octree = new List<int>();

        Color col;
        AddNode(Vector3.zero, new Vector3(16, 16, 16), out col);
    }

    int AddNode(Vector3 center, Vector3 halfsize, out Color col)
    {
        /* Fill the node starting at 'index' with information from inside the cube
         * at 'center +/- halfsize' */

        Vector3 quartersize = halfsize * 0.5f;
        int index = cpu_octree.Count;
        cpu_octree.Add(0);   /* mean color, will be filled below */
        for (int j = 0; j < 8; j++)
            cpu_octree.Add(0);   /* will be filled below */

        Color col_sum = new Color(0, 0, 0, 0);
        int col_count = 0;
        int i = index + 1;
        for (int z = -1; z <= 1; z += 2)
            for (int y = -1; y <= 1; y += 2)
                for (int x = -1; x <= 1; x += 2)
                    cpu_octree[i++] = GetOcTreeLink(center + new Vector3(x * quartersize.x,
                                                                         y * quartersize.y,
                                                                         z * quartersize.z),
                                                    quartersize, ref col_sum, ref col_count);
        if (col_count > 1)
            col_sum /= col_count;
        col = col_sum;
        cpu_octree[index] = Color2RGB(col);
        return index;
    }

    struct Triangle { internal Vector3[] p; internal Color c; }

    IEnumerable<Triangle> GetTriangles()
    {
        foreach (var rend in scene.GetComponentsInChildren<Renderer>())
        {
            var mesh = rend.GetComponent<MeshFilter>().sharedMesh;
            var triangles = mesh.triangles;
            var vertices = mesh.vertices;

            var vertices1 = new Vector3[vertices.Length];
            var tr = rend.transform;
            for (int i = 0; i < vertices.Length; i++)
                vertices1[i] = tr.TransformPoint(vertices[i]);

            var col = rend.sharedMaterial.color;

            for (int i = 0; i < triangles.Length; i += 3)
            {
                yield return new Triangle
                {
                    p = new Vector3[]
                    {
                        vertices1[triangles[i]],
                        vertices1[triangles[i + 1]],
                        vertices1[triangles[i + 2]],
                    },
                    c = col,
                };
            }
        }
    }

    bool Contains(Vector3[] tri, Vector3 center, Vector3 halfsize)
    {
        /* really, "does one vertex of the given triangle fall inside the box" */
        for (int i = 0; i < tri.Length; i++)
        {
            if (tri[i].x < center.x - halfsize.x) continue;
            if (tri[i].x > center.x + halfsize.x) continue;
            if (tri[i].y < center.y - halfsize.y) continue;
            if (tri[i].y > center.y + halfsize.y) continue;
            if (tri[i].z < center.z - halfsize.z) continue;
            if (tri[i].z > center.z + halfsize.z) continue;
            return true;
        }
        return false;
    }

    static int Color2RGB(Color c)
    {
        return (int)(c.r * 255.9) + ((int)(c.g * 255.9) << 8) + ((int)(c.b * 255.9) << 16);
    }

    int GetOcTreeLink(Vector3 center, Vector3 halfsize, ref Color col_sum, ref int col_count)
    {
        foreach (var tri in GetTriangles())
        {
            if (Contains(tri.p, center, halfsize))
            {
                if (halfsize.x < 0.05f)
                {
                    Color c = tri.c;
                    col_sum += c;
                    col_count += 1;
                    return (-0x80000000) | Color2RGB(c);
                }
                else
                {
                    Color col;
                    int result = AddNode(center, halfsize, out col);
                    col_sum += col;
                    col_count += 1;
                    return result;
                }
            }
        }
        return 0;
    }
}
