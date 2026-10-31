"""Geometry/transport invariants using synthetic, freely reproducible fixtures."""
import unittest
import numpy as np
from bake_level_relight import Bake,DT,filtered,stitch_small_charts,rtcore_scene,TriangleMesh

def plane(z,material):
    t=np.zeros(2,DT)
    t['v'][:,:,:3]=[[[-1000,-1000,z],[1000,-1000,z],[1000,1000,z]],
                     [[-1000,-1000,z],[1000,1000,z],[-1000,1000,z]]]
    t['v'][:,:,5]=-1;t['v'][:,:,6:]=.5;t['material']=material
    return t

def fixture(triangles,materials):
    b=Bake.__new__(Bake);b.t=np.concatenate(triangles);b.materials=materials
    b.alpha=np.array([m[3] for m in materials]);b.sky=np.array([m[2] for m in materials],bool)
    b.scene=rtcore_scene.EmbreeScene();verts=np.ascontiguousarray(b.t['v'][:,:,:3].reshape(-1,3))
    b.mesh=TriangleMesh(b.scene,verts,np.arange(len(verts),dtype=np.int32).reshape(-1,3))
    return b

def material(color=(255,255,255,255),alpha=-1,sky=False):
    return ('synthetic',np.array([[color]],np.uint8),int(sky),alpha)

class TransportTests(unittest.TestCase):
    def test_alpha_hole_transmits_to_next_surface(self):
        b=fixture([plane(1,0),plane(2,1)],[material((255,255,255,0),.5),material()])
        h=b.trace(np.array([[0,0,0]],np.float32),np.array([[0,0,1]],np.float32))
        self.assertEqual(b.t['material'][h['primID'][0]],1)

    def test_opaque_blocks_and_sky_illuminates(self):
        p=np.zeros((1,3),np.float32);n=np.array([[0,0,1]],np.float32)
        closed=fixture([plane(1,0)],[material()]).integrate(p,n,64)
        sky=fixture([plane(1,0)],[material(sky=True)]).integrate(p,n,64)
        self.assertLess(float(closed.max()),.01)
        np.testing.assert_allclose(sky[0],np.array([.90,.95,1.03])*.76,atol=.002)

    def test_diffuse_bounce_carries_surface_color(self):
        b=fixture([plane(1,0)],[material((255,20,20,255))])
        p=np.zeros((1,3),np.float32);n=np.array([[0,0,1]],np.float32)
        result=b.integrate(p,n,64,direct=np.full((1,128,128,3),.5,np.float32))
        self.assertGreater(float(result[0,0]),10*float(result[0,1]))
        self.assertGreater(float(result[0,0]),.1)

    def test_filter_does_not_leak_between_atlas_islands(self):
        c=np.full((1,128,128),-1,np.int32);v=np.zeros((1,128,128,3),np.float32)
        c[0,40:60,40:50]=1;c[0,40:60,50:60]=2
        v[0,40:60,40:50]=.2;v[0,40:60,50:60]=.9
        result=filtered(v,c)
        np.testing.assert_allclose(result[0,40:60,49],.2,atol=1e-6)
        np.testing.assert_allclose(result[0,40:60,50],.9,atol=1e-6)
        np.testing.assert_allclose(result[0,39,45],.2,atol=1e-6)

    def test_stitch_respects_facing_and_material(self):
        charts=np.full((1,128,128),-1,np.int32);charts[0,0,:2]=[1,2]
        positions=np.zeros((1,128,128,3),np.float32);positions[0,0,1,0]=1
        normals=np.zeros_like(positions);normals[0,0,0,2]=1;normals[0,0,1,2]=-1
        values=np.zeros_like(positions);values[0,0,1]=1
        triangles=np.zeros(2,DT);triangles['chart']=[1,2]
        actual=stitch_small_charts(values,positions,normals,charts,triangles)
        np.testing.assert_array_equal(actual,values)  # opposite wall sides
        normals[0,0,1,2]=1;triangles['material'][1]=1
        actual=stitch_small_charts(values,positions,normals,charts,triangles)
        np.testing.assert_array_equal(actual,values)  # different surface finish
        triangles['material'][1]=0
        actual=stitch_small_charts(values,positions,normals,charts,triangles)
        np.testing.assert_allclose(actual[0,0,:2],.5,atol=.001)

if __name__=='__main__':unittest.main()
