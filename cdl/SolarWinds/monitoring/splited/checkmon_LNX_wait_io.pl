#!/usr/bin/perl

# Time, in percentages, spent waiting for input/output (IO) operations.
# Note: Use the lowest threshold possible.
# If CPU waits IO is high, there may be problems with hard disk or problems with accessing NFS shares (if you use NFS).

use strict;
use warnings;

my @sa = split("\n", `LC_ALL=C vmstat`);

# this is to avoid a bug in the for loop if out is too short
if (@sa < 3) {
    print "Statistic: 100";
    print "Message.ERROR: vmstat output too short.\n";
    exit 1;
}

my @header = split(" ", $sa[1]);
my @data   = split(" ", $sa[2]);

# find the index of "wa"
my ($index) = grep { $header[$_] eq "wa" } 0..$#header;

if (defined $index) {
    my $wa = $data[$index];
    print "Statistic: $wa\n";
    print "Message: CPU wait IO in percentage: $wa\n";
    exit 0;
} else {
    print "Statistic: 100";
    print "Message.ERROR: Can't find CPU wait IO (wa) in output of -vmstat- command.\n";
    exit 1;
}
