using UnityEditor;
using UnityEngine;

public class FixTextureMaps : AssetPostprocessor
{
    // Fixes missing metallic map on import
    void OnPostprocessModel(GameObject g)
    {
        foreach (Renderer renderer in g.GetComponentsInChildren<Renderer>())
        {
            foreach (Material material in renderer.sharedMaterials)
            {
                string path = AssetDatabase.GetAssetPath(material.mainTexture);
                string directory = System.IO.Path.GetDirectoryName(path);
                string metallicMapPath = System.IO.Path.Combine(directory, g.name + "_MetallicGlossMap.png");

                if (System.IO.File.Exists(metallicMapPath))
                {
                    Texture metallicMap = AssetDatabase.LoadAssetAtPath<Texture>(metallicMapPath);
                    material.SetTexture("_MetallicGlossMap", metallicMap);
                    material.SetFloat("_Metallic", 1.0f);
                }
            }
        }
    }
}