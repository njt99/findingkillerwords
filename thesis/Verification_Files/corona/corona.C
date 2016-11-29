/*73:*/
#line 207 "glue.w"


#include "Codes.h"
#include <stdio.h>
#include "roundoff.h"

/*7:*/
#line 258 "verify.w"

const int MAXDEPTH= 200;

#line 1 "roundoff.w"
/*:7*/
#line 213 "glue.w"

/*5:*/
#line 194 "verify.w"

const char*inequalityFor(int code)
{
const int max_n_inequalities= 13200;
const int max_inequalities_size= 300000;
static int n_inequalities= 0;
static char inequalities[max_inequalities_size];
static char*inequalityIndex[max_n_inequalities];
if(n_inequalities==0){
FILE*fp= fopen("conditionlist","r");
if(fp==NULL){
fprintf(stderr,"can't open conditionlist\n");
exit(1);
}
int n_read= fread(inequalities,1,max_inequalities_size,fp);
char*ip= inequalities;
n_inequalities= 1;
inequalityIndex[n_inequalities++]= inequalities;
while(n_inequalities<max_n_inequalities&&ip<inequalities+n_read-1){
if(*ip=='\n')
inequalityIndex[n_inequalities++]= ip+1;
ip++;
}
fclose(fp);
}
if(code<1||code>=n_inequalities){
fprintf(stderr,"code %d out of range [1,%d] in inequalityFor\n",
code,n_inequalities);
exit(1);
}
return inequalityIndex[code];
}

/*:5*/
#line 214 "glue.w"

/*4:*/
#line 159 "verify.w"

#line 160 "verify.w"
void verify(char*where,int depth,int autocode)
{
int code;
if(depth>=MAXDEPTH){
where[depth]= '\0';
fprintf(stderr,"verify: fatal error at %s\n",where);
exit(1);
}
if(autocode==0){
scanf("%d",&code);
}else{
code= autocode;
}
where[depth]= '\0';
if(code<0){
printf("%s ",where);
}else if(code!=0&&inequalityHolds(inequalityFor(code),where,depth)){

}else{
where[depth]= '0';
verify(where,depth+1,code);
where[depth]= '1';
verify(where,depth+1,code);
}
}

/*:4*/
#line 215 "glue.w"

/*6:*/
#line 228 "verify.w"

main(int argc,char**argv)
{
if(argc!=2){
fprintf(stderr,"Usage: %s position < data\n",argv[0]);
exit(1);
}
char where[MAXDEPTH];
int depth;
for(depth= 0;argv[1][depth]!='\0';depth++){
if(argv[1][depth]!='0'&&argv[1][depth]!='1'){
fprintf(stderr,"bad position %s\n",argv[1]);
exit(1);
}
where[depth]= argv[1][depth];
}
where[depth]= '\0';

printf("verified corona %s - { ",where);
initialize_roundoff();
verify(where,depth,0);
if(!roundoff_ok()){
printf(". underflow may have occurred\n");
exit(1);
}

printf("}.\n");
exit(0);
}

/*:6*/
#line 216 "glue.w"
/*:73*/
