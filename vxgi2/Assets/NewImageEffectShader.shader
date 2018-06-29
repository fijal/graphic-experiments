Shader "Hidden/NewImageEffectShader"
{
    Properties{
        _MainTex("Base (RGB)", 2D) = "white" {}
    }
    SubShader{
        Pass{
            CGPROGRAM
            #pragma target 4.5
            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            sampler2D _MainTex;
            float4 _MainTex_ST;
            sampler2D _CameraDepthTexture;
            float4x4 _ViewProjectInverse;
            Buffer<int> g_OcTree;

            struct appdata {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f {
                float4 pos : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 worldDirection : TEXCOORD1;
            };
            
            v2f vert(appdata i)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(i.vertex);
                o.uv = i.uv;
                
                float4 D = mul(_ViewProjectInverse, float4(i.uv * 2 - 1, 0.5, 1));
                D.xyz /= D.w;
                D.xyz -= _WorldSpaceCameraPos;

                float4 D0 = mul(_ViewProjectInverse, float4(0, 0, 0.5, 1));
                D0.xyz /= D0.w;
                D0.xyz -= _WorldSpaceCameraPos;

                o.worldDirection = D.xyz / length(D0.xyz);

                return o;
            }

            float4 apply_node(float4 color, int node_index, float3 position, float halfsize)
            {
                while (1)
                {
                    int3 bits = int3((int)(position.x >= 0), (int)(position.y >= 0), (int)(position.z >= 0));
                    bits *= int3(1, 2, 4);
                    int value = g_OcTree.Load(node_index + bits.x + bits.y + bits.z);
                    if (value > 0)
                    {
                        halfsize *= 0.5;
                        position -= sign(position) * halfsize;
                        node_index = value;
                        /* loop again */
                    }
                    else
                    {
                        if (value < 0)
                        {
                            int3 rgb = int3(value, value >> 8, value >> 16);
                            rgb &= int3(0xff, 0xff, 0xff);
                            float4 color2 = float4(rgb * (1.0 / 255.0), 1.0);
                            color = lerp(color, color2, 0.5);
                        }
                        return color;
                    }
                }
            }

            float4 frag(v2f i) : COLOR 
            {
                float depth = SAMPLE_DEPTH_TEXTURE(_CameraDepthTexture, i.uv);
                depth = LinearEyeDepth(depth);

                float4 c = tex2D(_MainTex, i.uv);
                if (depth > 500)
                    return c;

                /* World position of some random point along this ray */
                float3 WD = i.worldDirection;

                /* Multiply by 'depth' */
                WD *= depth;

                /* That's our world-coordinate position! */
                float3 W = WD + _WorldSpaceCameraPos;

                
                
                const float INITIAL_HALFSIZE = 16;
                bool greater_min = all(W > float3(-INITIAL_HALFSIZE, -INITIAL_HALFSIZE, -INITIAL_HALFSIZE));
                bool lower_max = all(W < float3(INITIAL_HALFSIZE, INITIAL_HALFSIZE, INITIAL_HALFSIZE));
                if (all(bool2(greater_min, lower_max)))
                {
                    c = apply_node(c, 0, W, INITIAL_HALFSIZE);
                }
                return c;
            }
            ENDCG
        }
    }
}
