/*72:*/
#line 191 "glue.w"

#include "Codes.h"
#include "SL2ACJ.h"
#include "roundoff.h"
#include <stdio.h>

/*11:*/
#line 6 "Codes.w"

int inequalityHolds(const char*code,const char*where,int depth)
{
double pos[6],size[6],scale[6];
double min_d;
ACJ max_angle(0,0,0,0,0);
if(!covers_hole(where,depth,&min_d,&max_angle)){
return(1);
}
/*12:*/
#line 58 "Codes.w"

for(int i= 0;i<6;i++){
pos[i]= 0;
size[i]= 4;
scale[i]= pow(2,(5-i)/6.0);
}
for(int d= 0;d<depth;d++){
size[d%6]/= 2;
if(where[d]=='0'){
pos[d%6]-= size[d%6];
}else if(where[d]=='1'){
pos[d%6]+= size[d%6];
}else{
assert(0);
}
}
for(i= 0;i<6;i++){
pos[i]*= scale[i];
size[i]= (1+2*EPS)*(size[i]*scale[i]+HALFEPS*fabs(pos[i]));
}

/*:12*/
#line 15 "Codes.w"

ACJ along((XComplex(pos[0],pos[3])),XComplex(size[0],size[3]),0,0,0);
ACJ ortho((XComplex(pos[1],pos[4])),0,XComplex(size[1],size[4]),0,0);
ACJ whirle((XComplex(pos[2],pos[5])),0,0,XComplex(size[2],size[5]),0);
switch(code[0]){
case's':
return absUB(along)<1.10274;
case'l':
return absLB(along)>3.63201;
case'n':
return absUB(ortho)<min_d;
case'f':
ACJ angle= horizon(ortho);
return larger_angle(max_angle,angle);
case'W':
return absUB(whirle)<1;
case'w':
double wh= absLB(whirle);
return(1-EPS)*wh*wh>absUB(along);
default:
{
SL2ACJ g(evaluateWord(code+1,along,ortho,whirle));
ACJ l= length(g);
switch(code[0]){
case'O':
assert(0);return(0);
case'L':
return notIdentity(g)
&&absUB(l/along)<1
&&absLB(l*along)>1;
case'2':
return wordImpliesCommuting(code+1)
&&absUB(l/along)<1
&&absLB(l*along)>1;
default:
assert(0);return(0);
}
}
}
}

/*:11*/
#line 197 "glue.w"


/*13:*/
#line 79 "Codes.w"

SL2ACJ evaluateWord(const char*word,const ACJ&along,const ACJ&ortho,const ACJ&whirle)
{
ACJ one(1),zero(0);
SL2ACJ f(shortGenerator(along));
SL2ACJ w(closeGenerator(ortho,whirle));
SL2ACJ F(inverse(f));
SL2ACJ W(inverse(w));
SL2ACJ g(one,zero,zero,one);
int i;
for(i= 1;word[i]!=')';i++){
switch(word[i]){
case'w':g= g*w;break;
case'W':g= g*W;break;
case'f':g= g*f;break;
case'F':g= g*F;break;
default:assert(0);
}
}
return g;
}

/*:13*/
#line 199 "glue.w"


/*14:*/
#line 104 "Codes.w"

int wordImpliesCommuting(const char*word)
{
for(word++;word[0]!=')'&&word[1]!=')';word++){
if((word[0]=='f'&&word[1]=='f')
||(word[0]=='F'&&word[1]=='F')
||(word[0]=='w'&&word[1]=='w')
||(word[0]=='W'&&word[1]=='W')
||(word[0]=='f'&&word[1]=='w')
||(word[0]=='f'&&word[1]=='W')
||(word[0]=='F'&&word[1]=='w')
||(word[0]=='F'&&word[1]=='W'));
else return 0;
}
return 1;
}


/*:14*/
#line 201 "glue.w"


/*15:*/
#line 132 "Codes.w"


ACJ quarter(XComplex(0,1),0,0,0,0);
ACJ third(XComplex(-0.5,sqrt(0.75)),0,0,0,EPS);
ACJ vol3(XComplex(-0.3933,0.91942),0,0,0,1.415*EPS);

struct hole{
char*where;
double min_d;
ACJ max_angle;
}holes[]= {
{"0010001100011101100111010001101111101000101100001000111011010011010010001\
10101011000000100000",1,third},
{"0010001101010100101010101100011001011101111000011010101111001000000100011\
11100",1,third},
{"1110000000010001100110111011010110001111010111100011001111111001101100000\
000100010100010",1,third},
{"1110000000010001100110010011111010100111101101101111011000111111101101101\
0000111101",1,third},
{"1110000000010001100110010011111010101111100101100111010000110111100101100\
0000101101",1,third},
{"0010001101111100011010010101010110010110110101111011011000011011010001110\
100011101011001011101110111110100",1,vol3},
{"0010011101101100001010000101000110000110100101101011001000001011000001100\
100001101001001001101100111100100",1,vol3},
{"0010001100011101110011110001011111111011111001110011110000011110111101111",
1,third},
{"0010011100001101100011100001001111101011101001100011100000001110101101101",
1,third},
{"1110000000010001111111111101010011110111110101111111111100010010110001110",
1,third},
{"1110010000000001101111101101000011100111100101101111101100000010100001100",
1,third},
{0,0,0}
};

void compute_min_d(hole&h){
double pos[6],size[6],scale[6];
char*where= h.where;
int depth= strlen(where);
/*12:*/
#line 58 "Codes.w"

for(int i= 0;i<6;i++){
pos[i]= 0;
size[i]= 4;
scale[i]= pow(2,(5-i)/6.0);
}
for(int d= 0;d<depth;d++){
size[d%6]/= 2;
if(where[d]=='0'){
pos[d%6]-= size[d%6];
}else if(where[d]=='1'){
pos[d%6]+= size[d%6];
}else{
assert(0);
}
}
for(i= 0;i<6;i++){
pos[i]*= scale[i];
size[i]= (1+2*EPS)*(size[i]*scale[i]+HALFEPS*fabs(pos[i]));
}

/*:12*/
#line 172 "Codes.w"

ACJ ortho((XComplex(pos[1],pos[4])),0,XComplex(size[1],size[4]),0,0);
h.min_d= absLB(ortho);
}

int covers_hole(const char*where,int depth,double*min_d,ACJ*max_angle)
{
int i,j;
*min_d= 4;
*max_angle= quarter;
for(i= 0;holes[i].where;i++){
if(holes[i].min_d==1)compute_min_d(holes[i]);
if(holes[i].max_angle.f.re==vol3.f.re&&!strcmp(where,holes[i].where))
return(0);
int max_j= strlen(holes[i].where);
if(max_j>depth)max_j= depth;
for(j= 0;j<max_j&&j<depth;j+= 3)
if(where[j]!=holes[i].where[j])break;
if(j>=max_j){
if(holes[i].min_d<*min_d)*min_d= holes[i].min_d;
if(larger_angle(holes[i].max_angle,*max_angle))*max_angle= holes[i].max_angle;
}
}
return*min_d<=3;
}

/*:15*/
#line 203 "glue.w"

/*16:*/
#line 204 "Codes.w"

ACJ horizon(ACJ&ortho)
{
if(ortho.f.re<0)ortho= -ortho;
ACJ r= ortho*(ortho-6)+1;
ACJ d= (ortho*(-4)+4)*sqrt(-ortho);
AComplex x= r.f/d.f;
ACJ h(0,0,0,0,0);
if(x.z.re>0){
h= (r+d)/((ortho+1)*(ortho+1));
}else{
h= (r-d)/((ortho+1)*(ortho+1));
}
if(ortho.f.re<(1+EPS)*(size(ortho)+ortho.e))
h= ACJ(h.f,0,0,0,(1+EPS)*(size(h)+h.e));
return h;
}

/*:16*/
#line 204 "glue.w"

/*17:*/
#line 224 "Codes.w"

int larger_angle(ACJ&x,ACJ&y)
{
ACJ xy(0,0,0,0,0);
if(x.f.im>(1+EPS)*(size(x)+x.e)){
if(y.f.im>(1+EPS)*(size(y)+y.e))
xy= x/y;
if(-y.f.im>(1+EPS)*(size(y)+y.e))
xy= x*y;
}
if(-x.f.im>(1+EPS)*(size(x)+x.e)){
if(y.f.im>(1+EPS)*(size(y)+y.e))
xy= -x*y;
if(-y.f.im>(1+EPS)*(size(y)+y.e))
xy= -x/y;
}
return xy.f.im>(1+EPS)*(size(xy)+xy.e);
}
#line 1 "SL2ACJ.w"
/*:17*/
#line 205 "glue.w"


/*:72*/
