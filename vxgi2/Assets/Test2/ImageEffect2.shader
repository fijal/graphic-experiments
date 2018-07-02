Shader "Hidden/ImageEffect2"
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
            Texture3D _Rend3D;
            SamplerState sampler_Rend3D;

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

                /* Compute the local position for the Rend3D */
                //W -= float3(-0.8, 0, -1.2);
                W *= 32 / 32;

                float light_level_up = _Rend3D.Sample(sampler_Rend3D, W).a;
                c.r += light_level_up;
                
                return c;
            }
            ENDCG
        }
    }
}
