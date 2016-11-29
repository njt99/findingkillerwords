include Makefile.preamble
COMMON= ACJ.o Codes.o SL2ACJ.o Complex.o roundoff.o
CPLUSPLUS= g++
CC=gcc
TEX=tex
WEBOUT= \
	roundoff.h roundoff.c \
	Complex.h Complex.inline Complex.C \
	ACJ.h ACJ.inline ACJ.C \
	SL2ACJ.h SL2ACJ.C \
	Condition.h Condition.C \
	verify.C

WEBFILES= ACJ.w Codes.w Complex.w SL2ACJ.w glue.w roundoff.w verify.w

.SUFFIXES: .o .m .C .dvi .tex

.C.o:
	$(CPLUSPLUS) $(COPTS) $(CCFLAGS) -c ${@:o=C}

.tex.dvi:
	$(TEX) $<

verify: verify.o $(COMMON)
	$(CPLUSPLUS) $(COPTS) verify.o $(COMMON) $(LIBS) -o verify

depend:
	makedepend -I/usr/local/lib/g++-include -f Makefile.depend *.C
include Makefile.depend

$(WEBOUT): $(WEBFILES)
	ctangle verify
	rm verify.c

verify.tex: $(WEBFILES)
	cweave verify
  
# never optimize here, since the timing of arithmetic is important
test_float.o: test_float.C roundoff.h
	$(CPLUSPLUS) -g -c test_float.C

test_float: test_float.o roundoff.o roundoff.h
	$(CC) $(COPTS) test_float.o roundoff.o -o test_float -lm

# DO NOT DELETE THIS LINE -- make depend depends on it.
