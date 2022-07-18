s!{\\rm!{\\mathrm!g
s!{\\it!{\\mathit!g
s!{\\bf!{\\mathbf!g
s!{\\cal!{\\mathcal!g
s!\\mathbold!\\mathbf!
s!mathrm im !textit im !
s!mathrm re !textit re !
s!mathrm (an !textit (an !
s!mathit \([a-zA-Z][a-zA-Z][a-zA-Z]\)!textit \1!g
s!mathrm \((*[a-zA-Z][a-zA-Z][a-zA-Z]\)!textrm \1!g
s!mathbf \([a-zA-Z][a-zA-Z][a-zA-Z]\)!textbf \1!g
s!\\tt!\\texttt!g
s!{\\mathrm \([,-;:()]\) *}!{\\textrm \1}!g
/\\sectioncount/d
/\\theoremcount/d
s!\\proclaim{Theorem *\(.*\)}!\\begin{theorem}{\1}!
s!\\proclaim{Lemma *\(.*\)}!\\begin{lemma}{\1}!
s!\\proclaim{Proposition *\(.*\)}!\\begin{proposition}{\1}!
s!\\nonumproclaim{Proposition *\(.*\)}!\\begin{proposition}{\1}!
s!\\nonumproclaim{Lemma *\(.*\)}!\\begin{lemma}{\1}!
s!\\numbereddemo{Definition}!\\begin{definition}!
s!\\numbereddemo{{R}emarks*}!\\begin{remark}!
s!\\numbereddemo{Summary}!\\begin{summary}!
s!\\demo{Definition!\\begin{definition}{!
s!\\endproclaim!\\end{proposition}!
s!\\demo{Proof *\(.*\)}!\\begin{proof}{\1}!
s!\\enddemo!\\end{proof}!
s!\\elevensc *!!
s!\\matrix{\([^{}]*\)}!\\begin{matrix}\1\\end{matrix}!
s!\\matrix{!\\begin{matrix}!
s!\\ritem!\\item!
