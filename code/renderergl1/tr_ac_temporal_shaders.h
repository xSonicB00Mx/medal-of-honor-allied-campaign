/* GLSL 1.20 compatibility shaders, tested verbatim by the GPU regression. */
static const char *tmScreenVertex =
 "#version 120\n"
 "varying vec2 uv;void main(){uv=gl_Vertex.xy*.5+.5;gl_Position=gl_Vertex;}\n";
static const char *tmCameraFragment =
 "#version 120\n"
 "uniform sampler2D depthTexture;uniform int objectPass;uniform vec2 projectionScale,projectionOffset,depthReconstruct;\n"
 "uniform mat4 previousFromCurrent,previousProjection;varying vec2 uv;\n"
 "void main(){float d=texture2D(depthTexture,uv).r;\n"
 " if(objectPass==1){gl_FragColor=vec4(0.0,0.0,d,0.0);return;}\n"
 " float z=depthReconstruct.y/(2.0*d-1.0+depthReconstruct.x);\n"
 " vec4 p=vec4((uv*2.0-1.0+projectionOffset)*z/projectionScale,-z,1.0);\n"
 " if(d>=.999999){p=vec4(p.xyz/max(z,.001),0.0);}\n"
 " vec4 old=previousProjection*previousFromCurrent*p;\n"
 " gl_FragColor=vec4(old.xy/max(old.w,.0001)*.5+.5,d>=.999999?1.0:old.z/old.w*.5+.5,old.w>0.0?1.0:0.0);}\n";
static const char *tmObjectVertex =
 "#version 120\n"
 "uniform mat4 currentMVP,previousMVP,currentViewPrevious,weaponPrevious;uniform int weapon;\n"
 "varying vec4 oldClip,objectClip,currentClip;varying vec2 uv;\n"
 "void main(){currentClip=currentMVP*gl_Vertex;gl_Position=currentClip;uv=gl_MultiTexCoord0.xy;\n"
 " vec4 old=vec4(gl_MultiTexCoord1.xyz,1.0);oldClip=previousMVP*old;\n"
 " objectClip=weapon!=0?weaponPrevious*old:currentViewPrevious*old;}\n";
static const char *tmObjectFragment =
 "#version 120\n"
 "uniform sampler2D depthTexture,skin;uniform vec2 size;uniform float alphaCut,identity,valid,sampleRadius;uniform int objectPass,weapon,reactive;\n"
 "varying vec4 oldClip,objectClip,currentClip;varying vec2 uv;\n"
 "void main(){float a=texture2D(skin,uv).a;if(alphaCut>=0.0&&a<alphaCut)discard;\n"
 " float d=texture2D(depthTexture,gl_FragCoord.xy/size).r;\n"
 /* MSAA depth resolve selects an in-pixel sample, not necessarily its center.
  * Bound the difference by this triangle's depth slope over half a pixel.
  * A constant large epsilon would leak motion through nearby walls. */
 " float sampleTolerance=sampleRadius*(abs(dFdx(gl_FragCoord.z))+abs(dFdy(gl_FragCoord.z)));\n"
 " if(reactive!=0){if(gl_FragCoord.z>d+.00002+sampleTolerance||a<.02)discard;gl_FragColor=objectPass==1?vec4(0.0,0.0,d,-1.0):vec4(0.0);return;}\n"
 " if(abs(gl_FragCoord.z-d)>.000002+sampleTolerance)discard;\n"
 " if(objectPass==1){vec2 v=vec2(0.0);if(valid>.5&&objectClip.w>0.0)v=(currentClip.xy/currentClip.w-objectClip.xy/objectClip.w)*.5;\n"
 "  if(length(v*size)<.05)v=vec2(0.0);gl_FragColor=vec4(v,d,identity);}\n"
 " else{float z=oldClip.z/max(oldClip.w,.0001)*.5+.5;if(weapon!=0)z*=.3;\n"
 "  gl_FragColor=vec4(oldClip.xy/max(oldClip.w,.0001)*.5+.5,z,oldClip.w>0.0?valid:0.0);}}\n";
static const char *tmResolveFragment =
 "#version 120\n"
 "uniform sampler2D currentColor,oldColor,motion,objectData,oldData;uniform vec2 size,currentJitter,previousJitter;uniform float retention;varying vec2 uv;\n"
 "vec3 yc(vec3 c){return vec3(dot(c,vec3(.25,.5,.25)),(c.r-c.b)*.5,(-c.r+2.0*c.g-c.b)*.25);}\n"
 "vec3 rgb(vec3 c){return vec3(c.x+c.y-c.z,c.x+c.z,c.x-c.y-c.z);}\n"
 /* Nine bilinear fetches implement a separable 4x4 Catmull-Rom reconstruction.
  * Bilinear history alone progressively erases texture detail in still scenes. */
 "vec3 reconstruct(sampler2D image,vec2 t){vec2 p=t*size,c=floor(p-.5)+.5,f=p-c;\n"
 " vec2 w0=f*(-.5+f*(1.0-.5*f)),w1=1.0+f*f*(-2.5+1.5*f),w2=f*(.5+f*(2.0-1.5*f)),w3=f*f*(-.5+.5*f);\n"
 " vec2 w12=w1+w2,p0=(c-1.0)/size,p12=(c+w2/w12)/size,p3=(c+2.0)/size;vec3 s=vec3(0.0);\n"
 " s+=texture2D(image,vec2(p0.x,p0.y)).rgb*w0.x*w0.y;s+=texture2D(image,vec2(p12.x,p0.y)).rgb*w12.x*w0.y;s+=texture2D(image,vec2(p3.x,p0.y)).rgb*w3.x*w0.y;\n"
 " s+=texture2D(image,vec2(p0.x,p12.y)).rgb*w0.x*w12.y;s+=texture2D(image,vec2(p12.x,p12.y)).rgb*w12.x*w12.y;s+=texture2D(image,vec2(p3.x,p12.y)).rgb*w3.x*w12.y;\n"
 " s+=texture2D(image,vec2(p0.x,p3.y)).rgb*w0.x*w3.y;s+=texture2D(image,vec2(p12.x,p3.y)).rgb*w12.x*w3.y;s+=texture2D(image,vec2(p3.x,p3.y)).rgb*w3.x*w3.y;return clamp(s,0.0,1.0);}\n"
 "void main(){vec2 sampleUV=uv-currentJitter;vec3 current=reconstruct(currentColor,sampleUV);vec4 m=texture2D(motion,sampleUV),g=texture2D(objectData,sampleUV);\n"
 " if(retention<=0.0){gl_FragColor=vec4(current,1.0);return;}\n"
 " float w=retention;if(m.w<.5||g.w<0.0||any(lessThan(m.xy,.5/size))||any(greaterThan(m.xy,1.0-.5/size)))w=0.0;\n"
 " vec4 old=texture2D(oldData,m.xy);float tolerance=max(.000005,2.0*(abs(dFdx(m.z))+abs(dFdy(m.z))));\n"
 " if(abs(old.x-m.z)>tolerance||old.y!=g.w)w=0.0;\n"
 " vec3 lo=vec3(1e5),hi=vec3(-1e5),mean=vec3(0.0),second=vec3(0.0);\n"
 " for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){vec3 c=yc(texture2D(currentColor,sampleUV+vec2(float(x),float(y))/size).rgb);lo=min(lo,c);hi=max(hi,c);mean+=c;second+=c*c;}\n"
 " mean/=9.0;vec3 sigma=sqrt(max(second/9.0-mean*mean,vec3(0.0)));lo=max(lo,mean-1.25*sigma);hi=min(hi,mean+1.25*sigma);\n"
 /* Clip along the history-to-box-center ray rather than clamp channels
  * independently, which can create colored fringes. */
 " vec3 h=yc(reconstruct(oldColor,m.xy+previousJitter)),center=(hi+lo)*.5,extent=max((hi-lo)*.5,vec3(.0001));\n"
 " vec3 delta=h-center;float distance=max(max(abs(delta.x/extent.x),abs(delta.y/extent.y)),abs(delta.z/extent.z));\n"
 " h=center+delta/max(distance,1.0);\n"
 /* Reduce retention during motion and lighting changes, preserve high static
  * accumulation on subpixel geometry. Blend in approximately linear light. */
 " float speed=length((uv-m.xy)*size);w*=mix(1.0,.65,clamp(speed/8.0,0.0,1.0));\n"
 " vec3 history=clamp(rgb(h),0.0,1.0);float contrast=abs(yc(current).x-h.x);w*=1.0-clamp(contrast*2.0,0.0,.7);\n"
 " gl_FragColor=vec4(mix(current,history,w),1.0);}\n";
static const char *tmBlurFragment =
 "#version 120\n"
 "uniform sampler2D image,objectData;uniform vec2 size,currentJitter;uniform float shutter,diagnostic;varying vec2 uv;\n"
 "vec2 velocity(vec4 g){vec2 v=g.xy*size*shutter;float n=length(v);return g.w>0.0?v*min(1.0,32.0/max(n,.001)):vec2(0.0);}\n"
 "void main(){vec4 g=texture2D(objectData,uv-currentJitter);vec3 base=texture2D(image,uv).rgb;vec2 v=velocity(g);\n"
 " if(diagnostic>.5){gl_FragColor=vec4(abs(v)/32.0,0.0,1.0);return;}\n"
 " if(shutter<=0.0||g.w<0.0){gl_FragColor=vec4(sqrt(max(base,vec3(0.0))),1.0);return;}\n"
 /* A bounded neighbor search spreads moving silhouettes over the background.
  * Depth prevents a hidden moving actor from bleeding through a foreground
  * wall. A stationary pixel has zero velocity even during a camera pan. */
 " vec2 direction=v;float best=length(v);\n"
 " for(int ring=1;ring<=3;ring++)for(int k=0;k<8;k++){float angle=float(k)*.785398163;vec2 offset=vec2(cos(angle),sin(angle))*float(ring)*5.0;\n"
 "  vec4 n=texture2D(objectData,uv+offset/size-currentJitter);vec2 nv=velocity(n);float len=length(nv);\n"
 "  float along=abs(dot(offset,nv/max(len,.001))),across=abs(offset.x*nv.y-offset.y*nv.x)/max(len,.001);\n"
 "  if(n.z<=g.z+.000002&&len>best&&along<=len*.5+1.0&&across<2.5){best=len;direction=nv;}}\n"
 " if(best<.5){gl_FragColor=vec4(sqrt(max(base,vec3(0.0))),1.0);return;}\n"
 " vec3 sum=vec3(0.0);float total=0.0;\n"
 " for(int i=-8;i<=8;i++){vec2 offset=direction*(float(i)/16.0);vec2 t=uv+offset/size;\n"
 "  if(any(lessThan(t,vec2(0.0)))||any(greaterThan(t,vec2(1.0))))continue;\n"
 "  vec4 s=texture2D(objectData,t-currentJitter);vec2 sv=velocity(s);float len=length(sv);float w=0.0;\n"
 "  if(g.w>0.0&&length(v)>.5&&s.w==g.w)w=1.0;\n"
 "  else if(s.w>0.0&&len>.5&&s.z<=g.z+.000002){\n"
 "   float along=abs(dot(offset,sv/len)),across=abs(offset.x*sv.y-offset.y*sv.x)/len;w=clamp(len*.5+1.0-along,0.0,1.0)*clamp(1.5-across,0.0,1.0);}\n"
 "  else if(g.w>0.0&&length(v)>.5&&s.w>=0.0&&s.z>=g.z-.000002)w=1.0;\n"
 "  sum+=texture2D(image,t).rgb*w;total+=w;\n"
 " }\n"
 " vec3 result=total>0.0?sum/total:base;float coverage=clamp(total/17.0,0.0,1.0);\n"
 " gl_FragColor=vec4(sqrt(max(mix(base,result,g.w>0.0&&length(v)>.5?1.0:coverage),vec3(0.0))),1.0);}\n";
static const char *tmCopyFragment =
 "#version 120\n"
 "uniform sampler2D image;uniform int linearize;varying vec2 uv;void main(){vec4 c=texture2D(image,uv);gl_FragColor=linearize==2?vec4(c.z,c.w,0.0,1.0):linearize==1?vec4(c.rgb*c.rgb,1.0):c;}\n";
