#!/usr/bin/env -S -- perl -CASD -w

use English;
use File::Basename;
use autodie;
use strict;
use utf8;
use warnings;

my $dir = dirname(__FILE__);
my $lib = "$dir/../lib/perlcritic";

$ENV{PERL5LIB} = "$lib/lib/perl5";
exec( "$lib/bin/perltidy", @ARGV );
croak;
