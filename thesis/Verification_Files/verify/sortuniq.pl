while (<>) {
	$count{$_} += 1;
}

foreach (sort keys %count) {
	print "$count{$_} $_";
}
