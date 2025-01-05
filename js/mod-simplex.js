// Original implementation: A fast javascript implementation of simplex noise by Jonas Wagner

// Extensively modified, and minified. :>

(function(global){
    const SQRT3=Math.sqrt(3),SQRT5=Math.sqrt(5),F2=0.5*(SQRT3-1),G2=(3-SQRT3)/6,F3=1/3,G3=1/6,F4=(SQRT5-1)/4,G4=(5-SQRT5)/20;
    const fastFloor=x=>Math.floor(x)|0;
    const grad2=new Float64Array([1,1,-1,1,1,-1,-1,-1,1,0,-1,0,1,0,-1,0,0,1,0,-1,0,1,0,-1]);
    const grad3=new Float64Array([1,1,0,-1,1,0,1,-1,0,-1,-1,0,1,0,1,-1,0,1,-1,0,-1,0,-1,0,1,1,1,0,1,1,-1,0,1,-1,1,0,1,-1,-1,0,0,1,1,0,0,-1,1,0,0,1,-1,0,0,-1,-1,0,1,0,1,1,1,0,1,1,-1,0,1,-1,1,0,1,-1,-1,0,-1,1,1,0,-1,1,-1,0,-1,-1,1,0,-1,-1,-1,0]);
    const grad4=new Float64Array([
        0,1,1,1,0,1,1,-1,0,1,-1,1,0,1,-1,-1,0,-1,1,1,0,-1,1,-1,0,-1,-1,1,0,-1,-1,-1,
        1,0,1,1,1,0,1,-1,1,0,-1,1,1,0,-1,-1,-1,0,1,1,-1,0,1,-1,-1,0,-1,1,-1,0,-1,-1,
        1,1,0,1,1,1,0,-1,1,-1,0,1,1,-1,0,-1,-1,1,0,1,-1,1,0,-1,-1,-1,0,1,-1,-1,0,-1,
        1,1,1,0,1,1,-1,0,1,-1,1,0,1,-1,-1,0,-1,1,1,0,-1,1,-1,0,-1,-1,1,0,-1,-1,-1,0
    ]);
    function buildPermutationTable(random){
        const p=new Uint8Array(512);for(let i=0;i<256;i++)p[i]=i;for(let i=0;i<255;i++){const r=i+Math.floor(random()*(256-i));[p[i],p[r]]=[p[r],p[i]]}for(let i=256;i<512;i++)p[i]=p[i-256];return p;
    }
    function createNoise2D(random=Math.random){
        const perm=buildPermutationTable(random),permGrad2x=new Float64Array(perm).map(v=>grad2[(v%12)*2]),permGrad2y=new Float64Array(perm).map(v=>grad2[(v%12)*2+1]);
        return function(x,y){
            let n0=0,n1=0,n2=0,s=(x+y)*F2,i=fastFloor(x+s),j=fastFloor(y+s),t=(i+j)*G2,X0=i-t,Y0=j-t,x0=x-X0,y0=y-Y0;
            let i1,j1; if(x0>y0){i1=1;j1=0}else{i1=0;j1=1}
            const x1=x0-i1+G2,y1=y0-j1+G2,x2=x0-1+2*G2,y2=y0-1+2*G2,ii=i&255,jj=j&255;
            let t0=0.5-x0*x0-y0*y0;if(t0>=0){const gi0=ii+perm[jj],g0x=permGrad2x[gi0],g0y=permGrad2y[gi0];t0*=t0;n0=t0*t0*(g0x*x0+g0y*y0)}
            let t1=0.5-x1*x1-y1*y1;if(t1>=0){const gi1=ii+i1+perm[jj+j1],g1x=permGrad2x[gi1],g1y=permGrad2y[gi1];t1*=t1;n1=t1*t1*(g1x*x1+g1y*y1)}
            let t2=0.5-x2*x2-y2*y2;if(t2>=0){const gi2=ii+1+perm[jj+1],g2x=permGrad2x[gi2],g2y=permGrad2y[gi2];t2*=t2;n2=t2*t2*(g2x*x2+g2y*y2)}
            return 70*(n0+n1+n2);
        }
    }
    function createNoise3D(random=Math.random){
        const perm=buildPermutationTable(random),permGrad3x=new Float64Array(perm).map(v=>grad3[(v%12)*3]),permGrad3y=new Float64Array(perm).map(v=>grad3[(v%12)*3+1]),permGrad3z=new Float64Array(perm).map(v=>grad3[(v%12)*3+2]);
        return function(x,y,z){
            let n0=0,n1=0,n2=0,n3=0,s=(x+y+z)*F3,i=fastFloor(x+s),j=fastFloor(y+s),k=fastFloor(z+s),t=(i+j+k)*G3,X0=i-t,Y0=j-t,Z0=k-t,x0=x-X0,y0=y-Y0,z0=z-Z0;
            let i1,j1,k1,i2,j2,k2;if(x0>=y0){if(y0>=z0){i1=1;j1=0;k1=0;i2=1;j2=1;k2=0}else if(x0>=z0){i1=1;j1=0;k1=0;i2=1;j2=0;k2=1}else{i1=0;j1=0;k1=1;i2=1;j2=0;k2=1}}else{if(y0<z0){i1=0;j1=0;k1=1;i2=0;j2=1;k2=1}else if(x0<z0){i1=0;j1=1;k1=0;i2=0;j2=1;k2=1}else{i1=0;j1=1;k1=0;i2=1;j2=1;k2=0}}
            const x1=x0-i1+G3,y1=y0-j1+G3,z1=z0-k1+G3,x2=x0-i2+2*G3,y2=y0-j2+2*G3,z2=z0-k2+2*G3,x3=x0-1+3*G3,y3=y0-1+3*G3,z3=z0-1+3*G3,ii=i&255,jj=j&255,kk=k&255;
            let t_0=0.6-x0*x0-y0*y0-z0*z0;if(t_0>=0){const gi0=ii+perm[jj+perm[kk]],gx0=permGrad3x[gi0],gy0=permGrad3y[gi0],gz0=permGrad3z[gi0];t_0*=t_0;n0=t_0*t_0*(gx0*x0+gy0*y0+gz0*z0)}
            let t_1=0.6-x1*x1-y1*y1-z1*z1;if(t_1>=0){const gi1=ii+i1+perm[jj+j1+perm[kk+k1]],gx1=permGrad3x[gi1],gy1=permGrad3y[gi1],gz1=permGrad3z[gi1];t_1*=t_1;n1=t_1*t_1*(gx1*x1+gy1*y1+gz1*z1)}
            let t_2=0.6-x2*x2-y2*y2-z2*z2;if(t_2>=0){const gi2=ii+i2+perm[jj+j2+perm[kk+k2]],gx2=permGrad3x[gi2],gy2=permGrad3y[gi2],gz2=permGrad3z[gi2];t_2*=t_2;n2=t_2*t_2*(gx2*x2+gy2*y2+gz2*z2)}
            let t_3=0.6-x3*x3-y3*y3-z3*z3;if(t_3>=0){const gi3=ii+1+perm[jj+1+perm[kk+1]],gx3=permGrad3x[gi3],gy3=permGrad3y[gi3],gz3=permGrad3z[gi3];t_3*=t_3;n3=t_3*t_3*(gx3*x3+gy3*y3+gz3*z3)}
            return 32*(n0+n1+n2+n3);
        }
    }
    function createNoise4D(random=Math.random){
        const perm=buildPermutationTable(random),permGrad4x=new Float64Array(perm).map(v=>grad4[(v%32)*4]),permGrad4y=new Float64Array(perm).map(v=>grad4[(v%32)*4+1]),permGrad4z=new Float64Array(perm).map(v=>grad4[(v%32)*4+2]),permGrad4w=new Float64Array(perm).map(v=>grad4[(v%32)*4+3]);
        return function(x,y,z,w){
            let n0=0,n1=0,n2=0,n3=0,n4=0,s=(x+y+z+w)*F4,i=fastFloor(x+s),j=fastFloor(y+s),k=fastFloor(z+s),l=fastFloor(w+s),t=(i+j+k+l)*G4,X0=i-t,Y0=j-t,Z0=k-t,W0=l-t,x0=x-X0,y0=y-Y0,z0=z-Z0,w0=w-W0;
            let rankx=0,ranky=0,rankz=0,rankw=0;
            if(x0>y0){rankx++}else{ranky++}
            if(x0>z0){rankx++}else{rankz++}
            if(x0>w0){rankx++}else{rankw++}
            if(y0>z0){ranky++}else{rankz++}
            if(y0>w0){ranky++}else{rankw++}
            if(z0>w0){rankz++}else{rankw++}
            const i1=rankx>=3?1:0,j1=ranky>=3?1:0,k1=rankz>=3?1:0,l1=rankw>=3?1:0,i2=rankx>=2?1:0,j2=ranky>=2?1:0,k2=rankz>=2?1:0,l2=rankw>=2?1:0,i3=rankx>=1?1:0,j3=ranky>=1?1:0,k3=rankz>=1?1:0,l3=rankw>=1?1:0,
            x1=x0-i1+G4,y1=y0-j1+G4,z1=z0-k1+G4,w1=w0-l1+G4,x2=x0-i2+2*G4,y2=y0-j2+2*G4,z2=z0-k2+2*G4,w2=w0-l2+2*G4,x3=x0-i3+3*G4,y3=y0-j3+3*G4,z3=z0-k3+3*G4,w3=w0-l3+3*G4,x4=x0-1+4*G4,y4=y0-1+4*G4,z4=z0-1+4*G4,w4=w0-1+4*G4,
            ii=i&255,jj=j&255,kk=k&255,ll=l&255;
            let t0=0.6-x0*x0-y0*y0-z0*z0-w0*w0;if(t0>=0){const gi0=ii+perm[jj+perm[kk+perm[ll]]],gx0=permGrad4x[gi0],gy0=permGrad4y[gi0],gz0=permGrad4z[gi0],gw0=permGrad4w[gi0];t0*=t0;n0=t0*t0*(gx0*x0+gy0*y0+gz0*z0+gw0*w0)}
            let t1=0.6-x1*x1-y1*y1-z1*z1-w1*w1;if(t1>=0){const gi1=ii+i1+perm[jj+j1+perm[kk+k1+perm[ll+l1]]],gx1=permGrad4x[gi1],gy1=permGrad4y[gi1],gz1=permGrad4z[gi1],gw1=permGrad4w[gi1];t1*=t1;n1=t1*t1*(gx1*x1+gy1*y1+gz1*z1+gw1*w1)}
            let t2=0.6-x2*x2-y2*y2-z2*z2-w2*w2;if(t2>=0){const gi2=ii+i2+perm[jj+j2+perm[kk+k2+perm[ll+l2]]],gx2=permGrad4x[gi2],gy2=permGrad4y[gi2],gz2=permGrad4z[gi2],gw2=permGrad4w[gi2];t2*=t2;n2=t2*t2*(gx2*x2+gy2*y2+gz2*z2+gw2*w2)}
            let t3=0.6-x3*x3-y3*y3-z3*z3-w3*w3;if(t3>=0){const gi3=ii+i3+perm[jj+j3+perm[kk+k3+perm[ll+l3]]],gx3=permGrad4x[gi3],gy3=permGrad4y[gi3],gz3=permGrad4z[gi3],gw3=permGrad4w[gi3];t3*=t3;n3=t3*t3*(gx3*x3+gy3*y3+gz3*z3+gw3*w3)}
            let t4=0.6-x4*x4-y4*y4-z4*z4-w4*w4;if(t4>=0){const gi4=ii+1+perm[jj+1+perm[kk+1+perm[ll+1]]],gx4=permGrad4x[gi4],gy4=permGrad4y[gi4],gz4=permGrad4z[gi4],gw4=permGrad4w[gi4];t4*=t4;n4=t4*t4*(gx4*x4+gy4*y4+gz4*z4+gw4*w4)}
            return 27*(n0+n1+n2+n3+n4);
        }
    }
    global.SimplexNoise={
        createNoise2D:createNoise2D,
        createNoise3D:createNoise3D,
        createNoise4D:createNoise4D
    };
})(typeof window !== 'undefined' ? window : this);
