/*69:*/
#line 188 "glue.w"

#include "Codes.h"
#include "SL2ACJ.h"
#include "roundoff.h"
#include <stdio.h>

/*11:*/
#line 6 "Codes.w"

int inequalityHolds(const char*code,const char*where,int depth)
{
double pos[6],size[6],scale[6];
/*12:*/
#line 55 "Codes.w"

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
#line 10 "Codes.w"

ACJ along((XComplex(pos[0],pos[3])),XComplex(size[0],size[3]),0,0,0);
ACJ ortho((XComplex(pos[1],pos[4])),0,XComplex(size[1],size[4]),0,0);
ACJ whirle((XComplex(pos[2],pos[5])),0,0,XComplex(size[2],size[5]),0);
switch(code[0]){
case's':
return absUB(along)<1.10274;
case'l':
return absLB(along)>3.63201;
case'n':
return absUB(ortho)<1;
case'f':
return absLB(ortho)>3;
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
ACJ o= orthodist(g);
return absUB(o/ortho)<1
&&absLB(o*ortho)>1
&&notFPower(g);
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
#line 194 "glue.w"


/*13:*/
#line 76 "Codes.w"

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
#line 196 "glue.w"


/*14:*/
#line 101 "Codes.w"

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
#line 1 "SL2ACJ.w"
/*:14*/
#line 198 "glue.w"


/*:69*/
