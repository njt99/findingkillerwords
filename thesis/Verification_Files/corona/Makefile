include Makefile.preamble
COMMON= ACJ.o Codes.o SL2ACJ.o Complex.o roundoff.o
CPLUSPLUS= g++
CC=gcc
TEX=tex
CPLUSPLUSFILES= \
	roundoff.h \
	Complex.h Complex.inline Complex.C \
	ACJ.h ACJ.inline ACJ.C \
	SL2ACJ.h SL2ACJ.C \
	Condition.h Condition.C \
	corona.C

WEBFILES= ACJ.w Codes.w Complex.w SL2ACJ.w glue.w roundoff.w corona.w

.SUFFIXES: .o .m .C .dvi .tex

.C.o:
	$(CPLUSPLUS) $(COPTS) $(CCFLAGS) -c ${@:o=C}

.tex.dvi:
	$(TEX) $<

corona: corona.o $(COMMON)
	$(CPLUSPLUS) $(COPTS) corona.o $(COMMON) $(LIBS) -o corona

depend:
	makedepend -I/usr/local/lib/g++-include -f Makefile.depend *.C
include Makefile.depend

$(CPLUSPLUSFILES): $(WEBFILES)
	ctangle corona
	rm corona.c

corona.tex: $(WEBFILES)
	cweave corona

# DO NOT DELETE THIS LINE -- make depend depends on it.
