"""Offline diffuse sky + one-bounce transport pilot. Licensed inputs stay local.

The original baked artistic/point-light component is retained. This is not a
full replacement compiler: moving entities do not become permanent occluders.
No image-space data, camera, or screenshot is used by the bake.
"""
import argparse, hashlib, json, struct, sys, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'generated-local/CP09/relight-pilot'
sys.path.insert(0, str(WORK / 'python-deps'))
from embreex import rtcore_scene
from embreex.mesh_construction import TriangleMesh
from scipy import ndimage
from scipy.spatial import cKDTree

DT = np.dtype([('v', '<f4', (3, 10)), ('material', '<i4'),
               ('lm', '<i4'), ('chart', '<i4'), ('flags', '<i4')])

def fnv(data):
    h = 2166136261
    for b in data:
        h = ((h ^ b) * 16777619) & 0xffffffff
    return h

def normalize(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)

class Bake:
    def __init__(self, source):
        raw = (source / 'scene.bin').read_bytes()
        magic, count, mats, self.hash = struct.unpack_from('<4I', raw)
        assert magic == 0x31584541 and len(raw) == 16 + count * DT.itemsize
        self.t = np.frombuffer(raw, DT, offset=16)
        self.materials = []
        with (source / 'materials.bin').open('rb') as f:
            assert f.read(16) == raw[:16]
            for _ in range(mats):
                name = f.read(256).split(b'\0')[0].decode('latin1')
                w, h, sky, alpha = struct.unpack('<3if', f.read(16))
                tex = np.frombuffer(f.read(w*h*4), np.uint8).reshape(h,w,4)
                self.materials.append((name, tex, sky, alpha))
            assert not f.read(1)
        self.scene = rtcore_scene.EmbreeScene()
        verts = np.ascontiguousarray(self.t['v'][:,:,:3].reshape(-1,3))
        self.mesh = TriangleMesh(self.scene, verts,
            np.arange(len(verts), dtype=np.int32).reshape(-1,3))
        self.alpha = np.array([m[3] for m in self.materials])
        self.sky = np.array([m[2] for m in self.materials], bool)

    def texture(self, ids, u, v):
        t = self.t[ids]
        uv = t['v'][:,0,6:8]*(1-u-v)[:,None] + t['v'][:,1,6:8]*u[:,None] + t['v'][:,2,6:8]*v[:,None]
        out = np.empty((len(ids),4),np.float32)
        for mat in np.unique(t['material']):
            mask=t['material']==mat; tex=self.materials[mat][1];h,w=tex.shape[:2]
            # Repeat addressing matches diffuse world texture coordinates.
            x=np.floor(uv[mask,0]*w).astype(np.int64)%w
            y=np.floor(uv[mask,1]*h).astype(np.int64)%h
            out[mask]=tex[y,x]/255.
        return out

    def trace(self, origins, directions):
        """Alpha-tested cutouts transmit rays; sky terminates at the environment."""
        o=np.ascontiguousarray(origins,np.float32);d=np.ascontiguousarray(directions,np.float32)
        hit=self.scene.run(o,d,output=1)
        for _ in range(12):
            ids=hit['primID']; valid=np.flatnonzero(ids>=0)
            if not len(valid):break
            cut=valid[self.alpha[self.t['material'][ids[valid]]]>=0]
            if not len(cut):break
            rgba=self.texture(ids[cut],hit['u'][cut],hit['v'][cut])
            cut=cut[rgba[:,3] < self.alpha[self.t['material'][ids[cut]]]]
            if not len(cut):break
            o[cut]+=d[cut]*(hit['tfar'][cut,None]+.12)
            nex=self.scene.run(np.ascontiguousarray(o[cut]),np.ascontiguousarray(d[cut]),output=1)
            for k in hit:hit[k][cut]=nex[k]
        return hit

    def raster(self, count):
        shape=(count,128,128)
        pos=np.zeros(shape+(3,),np.float32);normal=np.zeros_like(pos)
        chart=np.full(shape,-1,np.int32)
        for tri in self.t:
            lm=tri['lm']
            if lm<0 or lm>=count or tri['flags']&1:continue
            uv=tri['v'][:,8:10]*128-.5
            lo=np.maximum(np.ceil(uv.min(0)-1e-4).astype(int),0)
            hi=np.minimum(np.floor(uv.max(0)+1e-4).astype(int),127)
            if np.any(hi<lo):continue
            x,y=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1))
            ab=uv[1]-uv[0];ac=uv[2]-uv[0];det=ab[0]*ac[1]-ab[1]*ac[0]
            if abs(det)<1e-8:continue
            px=x-uv[0,0];py=y-uv[0,1]
            u=(px*ac[1]-py*ac[0])/det;v=(ab[0]*py-ab[1]*px)/det
            ok=(u>=-1e-4)&(v>=-1e-4)&(u+v<=1.0001)
            x=x[ok];y=y[ok];u=u[ok,None];v=v[ok,None]
            interp=tri['v'][0]*(1-u-v)+tri['v'][1]*u+tri['v'][2]*v
            pos[lm,y,x]=interp[:,:3];normal[lm,y,x]=normalize(interp[:,3:6])
            chart[lm,y,x]=tri['chart']
        return pos,normal,chart

    def integrate(self, pos, normal, samples, direct=None, label='sky'):
        result=np.zeros((len(pos),3),np.float32)
        rng=np.random.default_rng(6031)
        rotations=rng.random(len(pos)).astype(np.float32)*2*np.pi
        # Tangent basis remains stable for coplanar surfaces.
        helper=np.zeros_like(normal);helper[:,2]=1
        helper[np.abs(normal[:,2])>.95]=[0,1,0]
        tangent=normalize(np.cross(helper,normal));bitangent=np.cross(normal,tangent)
        offset=pos+normal*.75
        sky_tint=np.array([.90,.95,1.03],np.float32)
        for s in range(samples):
            # Low discrepancy disk sequence, independently rotated per texel.
            r=np.sqrt((s+.5)/samples);angle=rotations+s*2.399963229728653
            d=tangent*(r*np.cos(angle))[:,None]+bitangent*(r*np.sin(angle))[:,None]+normal*np.sqrt(1-r*r)
            h=self.trace(offset.copy(),d)
            ids=h['primID'];hit=ids>=0
            sky=~hit
            sky[hit]=self.sky[self.t['material'][ids[hit]]]
            if direct is None:
                radiance=(.28+.72*np.maximum(d[:,2],0))[:,None]*sky_tint
                result+=radiance*sky[:,None]
            else:
                use=np.flatnonzero(hit&~sky)
                if len(use):
                    tri=self.t[ids[use]];u=h['u'][use];v=h['v'][use]
                    uv=tri['v'][:,0,8:10]*(1-u-v)[:,None]+tri['v'][:,1,8:10]*u[:,None]+tri['v'][:,2,8:10]*v[:,None]
                    lm=tri['lm'];good=(lm>=0)&(lm<len(direct))
                    incoming=np.full((len(use),3),.25,np.float32)
                    # Bilinear irradiance at the first diffuse bounce.
                    xy=np.clip(uv[good]*128-.5,0,127);ij=xy.astype(int);f=xy-ij
                    x=ij[:,0];y=ij[:,1];x1=np.minimum(x+1,127);y1=np.minimum(y+1,127);l=lm[good]
                    incoming[good]=direct[l,y,x]*(1-f[:,0,None])*(1-f[:,1,None])+direct[l,y,x1]*f[:,0,None]*(1-f[:,1,None])+direct[l,y1,x]*(1-f[:,0,None])*f[:,1,None]+direct[l,y1,x1]*f[:,0,None]*f[:,1,None]
                    albedo=np.clip(self.texture(ids[use],u,v)[:,:3]**1.7,.025,.8)
                    result[use]+=incoming*albedo
            if s%32==0 or s==samples-1:print(f'{label} {s+1}/{samples}',flush=True)
        return result/samples

def filtered(values, charts):
    """Denoise within charts; dilate gutters without mixing adjacent islands."""
    out=values.copy()
    for l in range(len(out)):
        valid=charts[l]>=0
        if not valid.any():continue
        for c in np.unique(charts[l][valid]):
            mask=charts[l]==c
            ys,xs=np.where(mask);y0=max(0,ys.min()-2);y1=min(128,ys.max()+3);x0=max(0,xs.min()-2);x1=min(128,xs.max()+3)
            m=mask[y0:y1,x0:x1].astype(np.float32)
            den=ndimage.gaussian_filter(m,.65)
            for k in range(3):
                val=ndimage.gaussian_filter(values[l,y0:y1,x0:x1,k]*m,.65)/np.maximum(den,1e-8)
                out[l,y0:y1,x0:x1,k][m>0]=val[m>0]
        dist,idx=ndimage.distance_transform_edt(~valid,return_indices=True)
        fill=(~valid)&(dist<=3)
        out[l][fill]=out[l][tuple(idx[:,fill])]
    return out

def stitch_small_charts(values, positions, normals, charts, triangles):
    """Reconstruct low-frequency irradiance across undersampled surface joins.

    Some original bevels occupy only two atlas texels. Filtering only inside
    their islands makes each bevel a separately lit rectangle. Gather nearby
    samples in WORLD space, restricted to matching material, compatible
    facing and plane distance. Opposite wall sides and unrelated materials
    must never participate. Large charts away from such joins are untouched.
    """
    valid=charts>=0;ids=charts[valid];p=positions[valid];n=normals[valid]
    count=np.bincount(ids);small=count[ids]<24
    material=np.full(len(count),-1,np.int32)
    for t in triangles:
        if t['chart']>=0 and t['lm']>=0:material[t['chart']]=t['material']
    tree=cKDTree(p);src=values[valid];dst=src.copy()
    for start in range(0,len(p),16384):
        stop=min(start+16384,len(p));q=p[start:stop]
        dist,idx=tree.query(q,k=32,distance_upper_bound=48)
        found=idx<len(p);idx=np.minimum(idx,len(p)-1)
        delta=p[idx]-q[:,None,:]
        aligned=np.sum(n[idx]*n[start:stop,None,:],axis=-1)>.8
        plane=np.abs(np.sum(delta*n[start:stop,None,:],axis=-1))<12
        same_material=material[ids[idx]]==material[ids[start:stop,None]]
        ok=found&aligned&plane&same_material
        other=ids[idx]!=ids[start:stop,None]
        joins=np.any(ok&other&(small[idx]|small[start:stop,None]),axis=1)
        w=np.exp(-dist*dist/(2*24*24))*ok
        average=np.sum(src[idx]*w[:,:,None],axis=1)/np.maximum(w.sum(1)[:,None],1e-9)
        dst[start:stop][joins]=average[joins]
    out=values.copy();out[valid]=dst
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=128)
    p.add_argument('--source',type=Path,default=ROOT/'profiles-local/CP09/relight-export/main/relight')
    p.add_argument('--out',type=Path,default=WORK/'bake-v1');p.add_argument('--reuse',action='store_true')
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);start=time.time()
    raw=(WORK/'m3l3.bsp').read_bytes();offset,length=struct.unpack_from('<2i',raw,12+2*8)
    original=np.frombuffer(raw[offset:offset+length],np.uint8).reshape(-1,128,128,3)
    b=Bake(a.source);assert fnv(original.tobytes())==b.hash
    geometry_hash=hashlib.sha256((a.source/'scene.bin').read_bytes()).hexdigest()
    materials_hash=hashlib.sha256((a.source/'materials.bin').read_bytes()).hexdigest()
    cache=WORK/('raster-'+geometry_hash[:16]+'.npz')
    if cache.exists():
        c=np.load(cache);pos,normal,chart=c['pos'],c['normal'],c['chart']
    else:
        pos,normal,chart=b.raster(len(original));np.savez_compressed(cache,pos=pos,normal=normal,chart=chart)
    valid=chart>=0;print(f'{valid.sum()} lightmap samples',flush=True)
    transport=a.out/'transport.npz'
    if a.reuse and transport.exists():
        c=np.load(transport)
        assert str(c['geometry_hash'])==geometry_hash and int(c['samples'])==a.samples and str(c['materials_hash'])==materials_hash and int(c['version'])==1, 'Stale bake cache'
        direct,bounce=c['direct'],c['bounce']
    else:
        direct=np.zeros_like(pos);direct[valid]=b.integrate(pos[valid],normal[valid],a.samples)
        direct=filtered(direct,chart)
        bounce=np.zeros_like(pos);bounce[valid]=b.integrate(pos[valid],normal[valid],a.samples,direct=direct,label='bounce')
        bounce=filtered(bounce,chart)
        np.savez_compressed(transport,direct=direct,bounce=bounce,geometry_hash=geometry_hash,materials_hash=materials_hash,samples=a.samples,version=1)
    # Stitch the transport, not the original texture or screenshot. Material
    # shaders duplicated for different lightmap pages share a material name.
    stitch_triangles=b.t.copy();names={};remap=[]
    for m in b.materials:
        if m[0] not in names:names[m[0]]=len(names)
        remap.append(names[m[0]])
    stitch_triangles['material']=np.array(remap)[b.t['material']]
    combined=stitch_small_charts(np.concatenate([direct,bounce],axis=-1),pos,normal,chart,stitch_triangles)
    direct=filtered(combined[:,:,:,:3],chart);bounce=filtered(combined[:,:,:,3:],chart)
    # Replace part of the old ambient solution, rather than multiplying its
    # existing shadows a second time. Map's ambient is 10; headroom is 127
    # before the engine's original overbright transform. One diffuse bounce
    # adds illumination in recesses instead of merely darkening their edges.
    lighting=.15*original+.85*(6+180*direct+190*bounce)
    lighting[~valid]=original[~valid]
    lighting=filtered(lighting,chart)
    payload=np.clip(np.rint(lighting),0,127).astype(np.uint8)
    # Unused atlas pixels and the moving-brush lightmaps remain byte-identical.
    padded=valid.copy()
    for l in range(len(padded)):
        if valid[l].any():padded[l]=ndimage.distance_transform_edt(~valid[l])<=3
    payload[~padded]=original[~padded]
    payload=payload.tobytes()
    factor=lighting/np.maximum(original,1)
    (a.out/'m3l3.aclm').write_bytes(struct.pack('<4I',0x314c4341,b.hash,len(payload),1)+payload)
    # Model irradiance probes: fixed offline samples, no runtime tracing.
    gridfile=a.out/'grid-transport.npz'
    step=128.;origin=np.floor(pos[valid].min(0)/step)*step-step
    maximum=np.ceil(pos[valid].max(0)/step)*step+step
    bounds=((maximum-origin)/step).astype(int)+1
    z,y,x=np.indices(tuple(bounds[::-1]));gp=np.stack([x,y,z],-1).reshape(-1,3).astype(np.float32)*step+origin
    direct_hash=hashlib.sha256(direct.tobytes()).hexdigest()
    reuse_grid=False
    if a.reuse and gridfile.exists():
        c=np.load(gridfile)
        reuse_grid=all(k in c for k in ['gd','gb','geometry_hash','materials_hash','direct_hash']) and str(c['geometry_hash'])==geometry_hash and str(c['materials_hash'])==materials_hash and str(c['direct_hash'])==direct_hash
        if reuse_grid:gd,gb=c['gd'],c['gb']
    if not reuse_grid:
        gn=np.zeros_like(gp);gn[:,2]=1
        gd=b.integrate(gp,gn,128,label='model sky')
        gb=b.integrate(gp,gn,128,direct=direct,label='model bounce')
        np.savez_compressed(gridfile,gd=gd,gb=gb,geometry_hash=geometry_hash,materials_hash=materials_hash,direct_hash=direct_hash)
    g=np.clip(.55+.65*(gd+.8*gb),.55,1.18).reshape(tuple(bounds[::-1])+(3,))
    # Probes are irradiance volumes, not geometry contact shadows.
    for k in range(3):g[:,:,:,k]=ndimage.gaussian_filter(g[:,:,:,k],.7)
    header=struct.pack('<4I4f3i',0x31474341,b.hash,1,3,*origin,step,*bounds)
    (a.out/'m3l3.acgrid').write_bytes(header+g.astype('<f4').tobytes())
    report=dict(map='m3l3',method='cosine-weighted diffuse sky visibility and one diffuse bounce',samples=a.samples,texels=int(valid.sum()),source_fnv=b.hash,
                geometry_sha256=geometry_hash,materials_sha256=materials_hash,small_chart_stitching=True,factor_percentiles=np.percentile(factor[valid],[0,10,50,90,100],axis=0).tolist(),grid_bounds=bounds.tolist(),seconds=time.time()-start)
    (a.out/'bake.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':main()
