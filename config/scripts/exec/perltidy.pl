#!/usr/bin/env -S -- perl

use File::Basename;
use autodie;
use diagnostics;
use strict;
use utf8;
use warnings;

my $dir = dirname(__FILE__);
my $lib = "$dir/../lib/perltidy";

$ENV{PERL5LIB} = "$lib/lib/perl5";
exec( "$lib/bin/perltidy", @ARGV );
croak;
