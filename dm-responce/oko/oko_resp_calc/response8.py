#! python2.7
# Example of a command line arguments:
#--out=output\mmdm15-37\  --actuators=mmdm15-37_actuators.txt --vias=mmdm15-37_vias.txt --via_size=21 --max_stroke=8e-6 --linewidth=8
#--out=output\mmdm15-39\  --actuators=mmdm15-39_actuators.txt --vias=mmdm15-39_vias.txt --via_size=0 --size=15 --aperture=15 --max_stroke=9.4e-6 --linewidth=4
#--out=output\mmdm15-17\  --actuators=mmdm15-17_actuators.txt --vias=mmdm15-17_vias.txt --via_size=21 --max_stroke=8e-6 --linewidth=8
#--out=output\mmdm30-59\  --actuators=mmdm30-59_actuators.txt --vias=mmdm30-59_vias.txt --size=30 --aperture=30 --via_size=18 --max_stroke=9e-6 --linewidth=8
#--out=output\mmdm30-39\  --actuators=mmdm30-39_actuators.txt --vias=mmdm30-39_vias.txt --size=30 --aperture=30 --via_size=18 --max_stroke=9e-6 --linewidth=8
#--out=output\mmdm30-79\  --actuators=mmdm30-79_actuators.txt --vias=mmdm30-79_vias.txt --size=30 --aperture=30 --via_size=18 --max_stroke=9e-6 --linewidth=8
#--out output\mmdm40-59\  --actuators=mmdm40-59_actuators.txt --vias=mmdm40-59_vias.txt --size=40 --aperture=40 --via_size=21 --max_stroke=15e-6 --linewidth=8
#--out output\mmdm40-79\  --actuators=mmdm40-79_actuators.txt --vias=mmdm40-79_vias.txt --size=40 --aperture=40 --via_size=21 --max_stroke=15e-6 --linewidth=8
#--out output\mmdm50-79\  --actuators=mmdm50-79_actuators.txt --vias=mmdm50-79_vias.txt --size=50 --aperture=50 --via_size=21 --max_stroke=30e-6 --linewidth=8
#--out output\mdm96\  --actuators=mdm96_actuators.txt --vias=mdm96_vias.txt --size=25.4 --aperture=25.4 --via_size=12 --max_stroke=19e-6 --linewidth=8

try:
    import IPython
    shell = IPython.get_ipython()
    shell.enable_matplotlib(gui='inline')
    inline_graphics=True
except:
    inline_graphics=False
  

import numpy as np
import re
from math import sqrt
from PIL import Image, ImageDraw, ImageFont
#%matplotlib inline
import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
import sys
import getopt
import os
import struct

# global model parameters
output_prefix=""
actuators_filename=""
vias_filename=""

grid=(201,201)
oversample_factor=16

#print grid
#sys.exit(0)

#grid=(1024, 1024)
size=15.0 # mm only one side is given, scale should be equal
mil=25.4/1000 # polygon data are in mils
bgcolor=0
fgcolor=255
aperture_r=15.0/2 # mm
max_stroke=8e-6 # m
via_size=12 # mil
linewidth_mil=0
linewidth_pixels=1

# antialiasing type for oversampling, BICUBIC produces more phisically accurate results
OVERSAMPLING_METHOD=Image.BICUBIC
#OVERSAMPLING_METHOD=Image.ANTIALIAS

def read_actuators(filename):
    actuators=[]
    if len(filename)<1:
        return actuators
    values=[re.sub("[^\d\.-]"," ",line).split() for line in open(filename,"r")]
    for line in values:
        polygon=[(float(line[i]),float(line[i+1])) for i in range(0,len(line)-1,2)]
        actuators.append(polygon)    
    return actuators    
 
def draw_actuator(image,polygon,layout=False):
    xc=grid_oversampled[0]/2.0
    yc=grid_oversampled[1]/2.0
    scale=grid_oversampled[0]*mil/size
    draw=ImageDraw.Draw(image) # define image context
    draw.polygon([(round(x*scale+xc,0),round(y*scale+yc,0)) for (x,y) in polygon],fill=fgcolor if not layout else "white",outline=fgcolor if not layout else "white")
    # draw lines with given thickness as well to make the representation closer to what is drawn in PCB
    vertices=list(range(0,len(polygon)-1))
    if polygon[0]!=polygon[len(polygon)-1]: # add first point if necessary
        vertices+=[0]
    for i in vertices:
        x0=round(polygon[i][0]*scale+xc,0)
        y0=round(polygon[i][1]*scale+yc,0)
        x1=round(polygon[i+1][0]*scale+xc,0)
        y1=round(polygon[i+1][1]*scale+yc,0)
        draw.line([x0,y0,x1,y1], fill=fgcolor if not layout else "white", width=linewidth_pixels)
        # line joins look ugly, so let us mask them with circles        
        r=int(round(linewidth_pixels/2.0,0))
        draw.ellipse((x0-r,y0-r,x0+r,y0+r),fill=(fgcolor) if not layout else "white")
        

def draw_via(image,vias_list,index,diameter):
    xc=grid_oversampled[0]/2.0
    yc=grid_oversampled[1]/2.0
    scale=grid_oversampled[0]*mil/size
    draw=ImageDraw.Draw(image)
#    print center
    if index>=len(vias_list): return;
    center=vias_list[index]
    draw.ellipse((round(xc+(center[0]-diameter/2.0)*scale,0),
                  round(yc+(center[1]-diameter/2.0)*scale,0),
                  round(xc+(center[0]+diameter/2.0)*scale,0),
                  round(yc+(center[1]+diameter/2.0)*scale,0)),
                  fill=(bgcolor),outline=bgcolor)
    

def draw_number(image,center,text):
    xc=grid_oversampled[0]/2.0
    yc=grid_oversampled[1]/2.0
    scale=grid_oversampled[0]*mil/size
    draw=ImageDraw.Draw(image)
    font=ImageFont.truetype("arialbd.ttf",60)
    xd=center[0]
    yd=center[1]
    r=sqrt(xd**2+yd**2)
    if abs(r)<0.001:
        r=1
        xd=-1
    xd/=r
    yd/=r
    #print xd,yd
    (xt,yt)=draw.textsize(text,font)
#    draw.text((round(xc+(center[0]+via_size*0.3)*scale,0),round(yc+(center[1]+via_size*0.3)*scale,0)),text,font=font, fill="red");
    draw.text((round(xc+(center[0]-xd*1.1*via_size)*scale-xt/2.0,0),round(yc+(center[1]-yd*1.1*via_size)*scale-yt/2.0,0)),text,font=font, fill="red");

              
def draw_aperture(image,layout=False):
    xc=grid_oversampled[0]/2.0
    yc=grid_oversampled[1]/2.0
    scale=grid_oversampled[0]/size
    draw=ImageDraw.Draw(image)
    draw.ellipse((round(xc-scale*aperture_r,0),round(yc-scale*aperture_r,0),
                  round(xc+scale*aperture_r,0),round(yc+scale*aperture_r,0)),
                  fill=(fgcolor) if not layout else None,
                  outline=fgcolor if not layout else "green")

def draw_grid(image):
    xc=grid_oversampled[0]/2.0
    yc=grid_oversampled[1]/2.0
    scale=grid_oversampled[0]/size
    draw=ImageDraw.Draw(image)
    ticks=[x-int(size/2)-1 for x in range(0,int(size+2))]
    dot_r=3
    for x in ticks: 
        for y in ticks:
            #draw.point([round(xc-scale*x,0),round(yc-scale*y,0)],fill="blue")
            draw.ellipse((round(xc-scale*x-dot_r,0),round(yc-scale*y-dot_r,0),
                        round(xc-scale*x+dot_r,0),round(yc-scale*y+dot_r,0)),
                       fill="blue", outline="blue")     
    # bounding box                   
    draw.line([0,0,grid_oversampled[0],0], width=6)
    draw.line([grid_oversampled[0],0,grid_oversampled[0],grid_oversampled[1]], width=6)
    draw.line([grid_oversampled[0],grid_oversampled[1],0,grid_oversampled[1]], width=6)
    draw.line([0,grid_oversampled[1],0,0], width=6)
                       
           
 
def calculate_response(act_image, boundary_image):
    signal=np.asarray(act_image,dtype=float)/fgcolor
    boundary=np.array(boundary_image,dtype=float)/fgcolor
    niter=int(1.0*grid[0]*grid[1])
    resp=np.zeros(grid,dtype=float)
    for n in range(0,niter):
        # Jacobi's method -- converges slow
        resp[1:-1,1:-1]=0.25*(resp[0:-2,1:-1]+resp[1:-1,0:-2]+resp[2:,1:-1]+resp[1:-1,2:]-signal[1:-1,1:-1])   
        resp=resp*boundary
    return resp    

def save_binary_header(filename):
    reserved=bytearray(16)
    with open(filename,"wb") as f:
        f.write(reserved)
        f.write(struct.pack("IIIf",len(actuators),grid[0],grid[1],float(aperture_r)))
    
def save_binary_response(response,filename):
    with open(filename,"ab") as f:
        response.astype(np.float32).tofile(f)
        
def report_parameters():
    print("Running with the following parameters.")
    print("actuators_filename=",actuators_filename)
    print("vias_filename=",vias_filename)
    print("output_prefix=",output_prefix)
    print("via_size=",via_size)
    print("grid=",grid)
    print("max_stroke=",max_stroke)
    print("size=",size)
    print("aperture_r=",aperture_r)
    print("oversample_factor=",oversample_factor)
    print("linewidth_mil=",linewidth_mil)
        
        
def save_layout():
    global size
    max_coordinate=0.0
    for i in range(0,len(actuators)):
        for (x,y) in actuators[i]:
            x=abs(x)
            y=abs(y)
            if x>max_coordinate: max_coordinate=x
            if y>max_coordinate: max_coordinate=y
    max_coordinate*=(2*mil);
    if aperture_r*2.0>max_coordinate: max_coordinate=aperture_r*2.0
    if max_coordinate>size: size=max_coordinate            
    layout=Image.new('RGB',grid_oversampled,"black")
    #print type(layout)
    #sys.exit(0)
    for i in range(0,len(actuators)):
        draw_actuator(layout,actuators[i],layout=True)
        draw_via(layout,vias,i,via_size)
        draw_number(layout,vias[i],str(i+1))
    draw_aperture(layout,layout=True)
    draw_grid(layout)
    aperture_mask=Image.new('RGBA',grid_oversampled,"black")
    backdrop=Image.new('RGB',grid_oversampled,"black")
    draw_aperture(aperture_mask,False)
    layout=Image.composite(backdrop,layout,aperture_mask)
    layout.save("%slayout.png"%output_prefix);
    if inline_graphics:
        print("Mirror layout")
        plt.figure(figsize=(15,15))
        plt.imshow(layout,cmap=None)
        plt.show()
    
#----------------  main ---------------------------------------------
# parse command line parameters
try:
    opts,args=getopt.getopt(sys.argv[1:],"",
     ["actuators=","vias=","out=", "via_size=","grid_size=","max_stroke=","size=","aperture=","oversample=","linewidth="])
except getopt.GetoptError:
    print("Usage: %s --actuators <filename> --vias <filename> --out <output prexix> --via_size <in mil> --grid_size <in pixels> --max_stroke <in m> --size <in mm> --aperture <in mm> --oversample <factor> --linewidth <width in mil>"%(sys.argv[0]))
    sys.exit(2)
for opt, arg in opts:
    if opt in ("--actuators"):
        actuators_filename=arg.strip()
    elif opt in ("--vias"):
        vias_filename=arg.strip()
    elif opt in ("--out"):
        output_prefix=arg.strip()
        # print "prefix=",output_prefix
    elif opt in  ("--via_size"):
        via_size=float(arg)
    elif opt in ("--grid_size"):
        grid=(int(arg),int(arg))
    elif opt in ("--max_stroke"):
        max_stroke=float(arg)
    elif opt in ("--size"):
        size=float(arg)
    elif opt in ("--aperture"):
        #print "aperture diameter=",arg
        aperture_r=float(arg)/2.0
        #print "aperture_r=",aperture_r
    elif opt in ("--oversample"):
        oversample_factor=int(arg)
    elif opt in ("--linewidth"):
        linewidth_mil=abs(float(arg))
            
# create output directory if required
output_directory=os.path.dirname(output_prefix)
if len(output_directory)>0:
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    elif not os.path.isdir(output_directory):
            print("Output directory is a regular file!")
            sys.exit(2)

report_parameters()

grid_oversampled=(oversample_factor*grid[0],oversample_factor*grid[1])
if linewidth_mil>0: 
    linewidth_pixels=int(round(oversample_factor*grid[0]*mil*linewidth_mil/size,0))
#print "linewidth_pixels=",linewidth_pixels
    
#read definitions for actuators and vias
actuators=read_actuators(actuators_filename)
vias=[x[0] for x in read_actuators(vias_filename)]

# generate an image of the actuators layout, for reference
save_layout()
#sys.exit("Exit after generating the figure")

# fill in the boundary
aperture=Image.new('L',grid_oversampled,(bgcolor))
draw_aperture(aperture)

# calculate normalization factor based on measured maximum stroke
acts=Image.new('L',grid_oversampled,(bgcolor))
# switch on all actuators
for i in range(0,len(actuators)):
    draw_actuator(acts,actuators[i])
    draw_via(acts,vias,i,via_size)


#acts.save('%sacts_doc.png'%output_prefix)
#aperture.save('%sapert_doc.png'%output_prefix)

acts=acts.resize(grid,OVERSAMPLING_METHOD)
aperture=aperture.resize(grid,OVERSAMPLING_METHOD)

#acts.save('%sacts.png'%output_prefix)
#aperture.save('%sapert.png'%output_prefix)

#  

#sys.exit(0)

norm=max_stroke/np.min(calculate_response(acts,aperture))

#sys.exit(0)


# output [dummy] initial shape: at the moment there is no way to simulate it
resp=np.zeros(grid,dtype=float)
np.savetxt("%s%03d.txt"%(output_prefix,0),resp)

binary_filename="%smmdm.bin"%(output_prefix)
save_binary_header(binary_filename)
save_binary_response(resp,binary_filename)

#fig=plt.figure(figsize = (10,10))
#plt.ion()
#plt.show(block=False) 
 
# calculate, show and output into text files responses for individual actuators
for i in range(0,len(actuators)):    
    acts=Image.new('L',grid_oversampled,(bgcolor))
    draw_actuator(acts,actuators[i])
    draw_via(acts,vias,i,via_size)
    acts=acts.resize(grid,OVERSAMPLING_METHOD)

    resp=-norm*calculate_response(acts,aperture)
    print("actuator ",i)
    np.savetxt("%s%03d.txt"%(output_prefix,i+1),resp)
    save_binary_response(resp,binary_filename)
    
    min_val=np.min(resp)
    resp_byte=np.zeros(grid,dtype=np.uint8)
    for x,y in np.nditer([resp,resp_byte],op_flags=['readwrite']):
       y[...]=int(x*255.0/min_val)
    
    resp_img=Image.fromarray(np.array(resp_byte,dtype=np.uint8),"L")
    
    if inline_graphics:
        fig=plt.figure(figsize = (15,15))
        fig.add_subplot(3,3,1)
        plt.imshow(acts,cmap='gray')
        fig.add_subplot(3,3,2)
        plt.imshow(aperture,cmap='gray')
        fig.add_subplot(3,3,3)
        plt.imshow(resp_img,cmap='gray')
        plt.show()
        #plt.draw()
        #plt.pause(0.1)

