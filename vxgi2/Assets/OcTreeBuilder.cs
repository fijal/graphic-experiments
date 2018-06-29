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

    int AddEmptyNode()
    {
        int result = cpu_octree.Count;
        for (int i = 0; i < 8; i++)
            cpu_octree.Add(0);
        return result;
    }

    void BuildCpuOcTree()
    {
        cpu_octree = new List<int>();
        AddNode(Vector3.zero, new Vector3(16, 16, 16));
    }

    int AddNode(Vector3 center, Vector3 halfsize)
    {
        /* Fill the node starting at 'index' with information from inside the cube
         * at 'center +/- halfsize' */

        Vector3 quartersize = halfsize * 0.5f;
        int index = cpu_octree.Count;
        for (int j = 0; j < 8; j++)
            cpu_octree.Add(0);   /* will be fixed below */

        int i = index;
        for (int z = -1; z <= 1; z += 2)
            for (int y = -1; y <= 1; y += 2)
                for (int x = -1; x <= 1; x += 2)
                    cpu_octree[i++] = GetOcTreeLink(center + new Vector3(x * quartersize.x,
                                                                         y * quartersize.y,
                                                                         z * quartersize.z),
                                                    quartersize);
        return index;
    }

    IEnumerable<Vector3[]> GetTriangles()
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

            for (int i = 0; i < triangles.Length; i += 3)
            {
                yield return new Vector3[]
                {
                    vertices1[triangles[i]],
                    vertices1[triangles[i + 1]],
                    vertices1[triangles[i + 2]],
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

    int GetOcTreeLink(Vector3 center, Vector3 halfsize)
    {
        foreach (var tri in GetTriangles())
        {
            if (Contains(tri, center, halfsize))
            {
                if (halfsize.x < 0.05f)
                {
                    int random_color = Random.Range(0, 0x1000000);
                    return (-0x80000000) | random_color;
                }
                else
                {
                    return AddNode(center, halfsize);
                }
            }
        }
        return 0;
    }
}
