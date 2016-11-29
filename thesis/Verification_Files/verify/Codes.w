@*Proving inequalities.
\lemma
If inequalityHolds|(what,where)| returns |1|, then $Z(|where|)$ is MNG-free.
\endlemma

@<Definition of |inequalityHolds|@>=
int inequalityHolds(const char* code, const char* where, int depth)
{
  double pos[6], size[6], scale[6];
  @<Find |pos| and |size| of |where,depth|@>@;
  ACJ along ( (XComplex(pos[0],pos[3])), XComplex(size[0],size[3]),0,0, 0);
  ACJ ortho ( (XComplex(pos[1],pos[4])), 0,XComplex(size[1],size[4]),0, 0);
  ACJ whirle( (XComplex(pos[2],pos[5])), 0,0,XComplex(size[2],size[5]), 0);
  switch(code[0]) {
  case 's':      // short :            $\abs{|along|} < e^{0.0978...}$
    return absUB(along) < 1.10274;
  case 'l':      // long :             $\abs{|along|} > e^{1.28978...}$
    return absLB(along) > 3.63201;
  case 'n':      // near :             $\abs{|ortho|} < 1$
    return absUB(ortho) < 1;
  case 'f':      // far :              $\abs{|ortho|} > 3$
    return absLB(ortho) > 3;
  case 'W':      // whirle small :     $\abs{|whirle|} < 1$
    return absUB(whirle) < 1;
  case 'w':      // whirle big :    $\abs{|whirle|^2} > \abs{|along|}$
    double wh = absLB(whirle);
    return (1-EPS)*wh*wh > absUB(along);
  default:
    {
      SL2ACJ g(evaluateWord(code+1, along,ortho,whirle));
      ACJ l = length(g);
      switch(code[0]) {
      case 'O': // ortho :         $\abs{|ortho|(g)} < \abs{|ortho|(w)}$ and $g$ not a power of $f$
        ACJ o = orthodist(g);
	return absUB(o / ortho) < 1
	    && absLB(o * ortho) > 1
	    && notFPower(g);
      case 'L': // length :       $\abs{|length|(g)} < \abs{|length|(w)}$ and $g$ nontrivial
	return notIdentity(g)
	    && absUB(l/along) < 1
	    && absLB(l*along) > 1;
      case '2': // identity :     $\abs{|length|(g)} < \abs{|length|(w)}$ and |code| is simple
	return wordImpliesCommuting(code+1)
	    && absUB(l/along) < 1
	    && absLB(l*along) > 1;
      default:
        assert(0); return(0);
      }
    }
  }
}

@ We may take the values of scale to be exact, since $pow(2, (5-i)/6.0)$ takes
the same values on all of the machines on which the program was run.
@<Find |pos| and |size| of |where,depth|@>=
  for (int i = 0; i < 6; i++) {
    pos[i] = 0;
    size[i] = 4;
    scale[i] = pow(2, (5-i) / 6.0);
  }
  for (int d = 0; d < depth; d++) {
    size[d%6] /= 2;
    if (where[d] == '0') {
      pos[d%6] -= size[d%6];
    } else if (where[d] == '1') {
      pos[d%6] += size[d%6];
    } else {
      assert(0);
    }
  }
  for (i = 0; i < 6; i++) {
    pos[i] *= scale[i];
    size[i] = (1+2*EPS)*(size[i]*scale[i] + HALFEPS*fabs(pos[i]));
  }

@ @<Definition of |evaluateWord|@>=
SL2ACJ evaluateWord(const char* word, const ACJ& along, const ACJ& ortho, const ACJ& whirle)
{
  ACJ one(1), zero(0);
  SL2ACJ f(shortGenerator(along));
  SL2ACJ w(closeGenerator(ortho,whirle));
  SL2ACJ F(inverse(f));
  SL2ACJ W(inverse(w));
  SL2ACJ g(one,zero,zero,one);
  int i;
  for (i = 1; word[i] != ')'; i++) {
    switch(word[i]) {
    case 'w': g = g*w; break;
    case 'W': g = g*W; break;
    case 'f': g = g*f; break;
    case 'F': g = g*F; break;
    default: assert(0);
    }
  }
  return g;
}

@ For any integers $k,l$, $f^k w^l = 1$ implies that $f$ and $w$ commute.
If |wordImpliesCommuting(word)| returns $1$, then $word$
is of the form $f^k w^l$.
@<Definition of |wordImpliesCommuting|@>=
int wordImpliesCommuting(const char* word)
{
  for (word++; word[0] != ')' && word[1] != ')'; word++) {
    if ((word[0] == 'f' && word[1] == 'f')
     || (word[0] == 'F' && word[1] == 'F')
     || (word[0] == 'w' && word[1] == 'w')
     || (word[0] == 'W' && word[1] == 'W')
     || (word[0] == 'f' && word[1] == 'w')
     || (word[0] == 'f' && word[1] == 'W')
     || (word[0] == 'F' && word[1] == 'w')
     || (word[0] == 'F' && word[1] == 'W')) ; /* word is OK -- keep checking */
    else return 0;
  }
  return 1;
}
