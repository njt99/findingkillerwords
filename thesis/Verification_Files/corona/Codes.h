/*71:*/
#line 178 "glue.w"

#ifndef _Codes_h_
#define Codes_h_
#include "roundoff.h"
#include "SL2ACJ.h"
int inequalityHolds(const char*code,const char*where,int depth);
SL2ACJ evaluateWord(const char*word,const ACJ&along,const ACJ&ortho,const ACJ&whirle);
int wordImpliesCommuting(const char*word);
int covers_hole(const char*where,int depth,double*min_d,ACJ*max_angle);
ACJ horizon(ACJ&ortho);
int larger_angle(ACJ&x,ACJ&y);
#endif

/*:71*/
