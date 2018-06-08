open CN, "<conditionlist";
@conditions = <CN>;
close CN;
@cl = map { length $_ } @conditions;

open AC, "<appearancecounts";
while (<AC>) {
	$line = $_;
	chomp $line;
	($cnt, $cond) = split(/ /, $line);
	$cndl = @cl[$cond] - 2;
	print "$cnt $cond $cndl\n";
}
