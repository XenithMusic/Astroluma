#version 330

// Input vertex attributes (from vertex shader)
in vec2 fragTexCoord;
in vec4 fragColor;

// Input uniform values
uniform sampler2D texture0;
uniform vec4 colDiffuse;
uniform float time;
uniform vec2 resolution;

// Output fragment color
out vec4 finalColor;

// NOTE: Add your custom variables here

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

vec2 hash22(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)),
             dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f*f*(3.0 - 2.0*f); // smoothstep
    float a = hash(i + vec2(0,0));
    float b = hash(i + vec2(1,0));
    float c = hash(i + vec2(0,1));
    float d = hash(i + vec2(1,1));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float simplexNoise(vec2 p) {
    const float K1 = 0.366025403; // (sqrt(3)-1)/2
    const float K2 = 0.211324865; // (3-sqrt(3))/6
    
    vec2 i = floor(p + (p.x + p.y) * K1);
    
    vec2 a = p - (i - (i.x + i.y) * K2);
    vec2 o = (a.x < a.y) ? vec2(0.0, 1.0) : vec2(1.0, 0.0);
    vec2 b = a - o + K2;
    vec2 c = a - 1.0 + 2.0 * K2;
    
    vec3 h = max(0.5 - vec3(dot(a,a), dot(b,b), dot(c,c)), 0.0);
    vec3 n = h * h * h * h * vec3(dot(a, hash22(i)), 
                                 dot(b, hash22(i + o)), 
                                 dot(c, hash22(i + 1.0)));
    
    return dot(n, vec3(70.0)); // range ≈ [-1, 1] → multiply to taste
}

void main()
{
    // Texel color fetching from texture sampler
    vec4 texelColor = texture(texture0, fragTexCoord);
    vec2 uvRaw = gl_FragCoord.xy/resolution.xy;
    vec2 uv = uvRaw;
    uv.x *= (resolution.x/resolution.y);

    float sunAngle = fract((time)+0.55) * -6.28319;
    float sunHeight = (sin(sunAngle)-0.5)*1.5;
    float sunCross = (cos(sunAngle)*1.5+0.75)*0.85;

    vec3 dayTop = vec3(0.4,0.7,1.0);
    vec3 dayBottom = vec3(0.8,0.9,1.0);
    vec3 nightTop = vec3(0.01,0.0,0.04);
    vec3 nightBottom = vec3(0.04,0.02,0.08);
    vec3 sunrise = vec3(1.0,0.6,0.3)*1.2;

    float skyMix = smoothstep(-0.5,0.5,sunHeight);
    vec3 topColor = mix(nightTop,dayTop,skyMix);
    vec3 bottomColor = mix(nightBottom,dayBottom,skyMix);
    float sunriseMask = smoothstep(-0.68,0.1,sunHeight)
                      * smoothstep(1.0,0.2,sunHeight);
    bottomColor = mix(bottomColor,sunrise,sunriseMask);

    float horizonY = 0.5 + uv.y * 0.5;
    vec3 skyColor = mix(bottomColor,topColor,horizonY);

    vec2 sunPosUV = vec2(sunCross,sunHeight);

    float distance = length(uv-sunPosUV);
    skyColor += max(0,min(1,0.03/distance));

    // NOTE: Implement here your fragment shader code

    // final color is the color from the texture 
    //    times the tint color (colDiffuse)
    //    times the fragment color (interpolated vertex color)
    // finalColor = texelColor*colDiffuse*fragColor;
    vec2 center = vec2(resolution.x/2,-resolution.x/2);
    float angle = -sunAngle/2;
    vec2 rot = vec2(cos(angle), sin(angle));
    mat2 rotMatrix = mat2(rot.x, -rot.y, rot.y, rot.x);

    vec2 uv1 = (gl_FragCoord.xy-center) * rotMatrix + center;
    vec2 uv2 = (gl_FragCoord.xy-center) * rotMatrix * 1.7 + center;

    uv1 *= (resolution.x/resolution.y)*(3/resolution.x);
    uv2 *= (resolution.x/resolution.y)*(3/resolution.x);

    skyColor += pow(max(0.01,simplexNoise(uv1*35.3211+35)/2+0.5),32.0)*(1.0-skyMix);
    skyColor += pow(max(0.01,simplexNoise(uv2*28.59+-12)/2+0.5),24.0)*0.25*(1.0-skyMix);
    finalColor = vec4(skyColor,1);
}
