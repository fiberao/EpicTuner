var fs = require('fs');
 RECx=[];
 RECy=[];
function tl_mirror_map(input){
	acturator_menbrane_view=true;
	///RECORDERS
	var RECi=0;

	var RECz=[];
	///
	var hexmap_x=25;
	var hexmap_y=25;
	
	var test=[];
	for (var x=-hexmap_x;x<=hexmap_x;x++){
		for (var y=-hexmap_y;y<=hexmap_y;y++){
			var r=Math.sqrt(x*x+y*y);
			r=r/hexmap_x;
			var theta=Math.atan2(y, x)  / (2.0*Math.PI)+0.5;
			var ring=0;
			if (Math.floor(r*10)<9) {
				 ring=24+Math.ceil(theta*16);
			}
			if (Math.floor(r*10)<6) {
				 ring=8+Math.ceil(theta*16);
			}
			if (Math.floor(r*10)<3){
				 ring=0+Math.ceil(theta*8);
			}
			if (ring>40 || ring<0){
				//console.log(ring)
			}
			test[(x+hexmap_x)+(y+hexmap_y)*(hexmap_x*2)]=input[ring];
		}
	}
	// smooth filter
	var smooth_l=4;
	for (var x=0;x<2*hexmap_x;x++) 
		for (var y=0;y<2*hexmap_y;y++) {
			//get center
			var xfix=x-hexmap_x+smooth_l/2;
			var yfix=y-hexmap_y+smooth_l/2;
			var r=Math.sqrt(xfix*xfix+yfix*yfix);
			var holding_radius=hexmap_x*9/10;
			var R=200; 
			if (acturator_menbrane_view){
				//smooth 
				var sum=0;
				for (var sx=0;sx<smooth_l;sx++) 
					for (var sy=0;sy<smooth_l;sy++) 
						sum+=test[(y+sy)*(hexmap_x*2)+x+sx];
				sum/=smooth_l*smooth_l;
				//hemi-sphere correction
				var height=Math.sqrt(R*R-r*r)-Math.sqrt(R*R-holding_radius*holding_radius);
				var height_r0= Math.sqrt(R*R)-Math.sqrt(R*R-holding_radius*holding_radius);
				var corrected = sum-input[0];
				corrected=corrected*(height/height_r0)+input[0];
			}else{
				var corrected = test[(y+smooth_l/2)*(hexmap_x*2)+x+smooth_l/2];
			}
			//surface holder correction
			var z1=input[41];var x1=holding_radius*Math.sin(Math.PI*0+Math.PI*1/2+Math.PI);var y1=holding_radius*Math.cos(Math.PI*0+Math.PI*1/2+Math.PI);
			var z2=input[42];var x3=holding_radius*Math.sin(Math.PI*2/3+Math.PI*1/2+Math.PI);var y3=holding_radius*Math.cos(Math.PI*2/3+Math.PI*1/2+Math.PI);
			var z3=input[43];var x2=holding_radius*Math.sin(-Math.PI*2/3+Math.PI*1/2+Math.PI);var y2=holding_radius*Math.cos(-Math.PI*2/3+Math.PI*1/2+Math.PI);
			var zfix=(x3*y2*z1 - xfix*y2*z1 - x2*y3*z1 + xfix*y3*z1 + x2*yfix*z1 - x3*yfix*z1 - x3*y1*z2 + xfix*y1*z2 +  x1*y3*z2 - xfix*y3*z2 - x1*yfix*z2 + x3*yfix*z2 + x2*y1*z3 - xfix*y1*z3 - x1*y2*z3 + xfix*y2*z3 + x1*yfix*z3 - x2*yfix*z3)/(x2*y1 - x3*y1 - x1*y2 + x3*y2 + x1*y3 - x2*y3);
			corrected+=(zfix)*1/3;
			corrected-=25;
			//aperature cut 
			if (r<=holding_radius){
				console.log(x , " ",y)
				RECx[RECi]=x*2/45.0-1.0;
				RECy[RECi]=y*2/45.0-1.0;
				RECz[RECi]=corrected;
				RECi+=1;
				
			}
		}
		return RECz;
}
function zeros(except){
		var a=[];
		for (var i =0;i<44;i++){
			a[i]=0
		}
		a[except]=1;
		return a;
}
RECacts=[]
for (var act=0;act<43;act++){
	if (act<3){
		console.log(zeros(act+41))
		RECacts[act]=tl_mirror_map(zeros(act+41));
	}else{
		console.log(zeros(act-3+1))
		RECacts[act]=tl_mirror_map(zeros(act-3+1));
	}
	
}
fs.writeFile("ir.txt", JSON.stringify(RECacts))
fs.writeFile("wfx.txt", JSON.stringify(RECx))
fs.writeFile("wfy.txt", JSON.stringify(RECy))