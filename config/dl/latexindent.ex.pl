#!/usr/bin/env -S -- perl -CASD

use English;
use File::Basename;
use autodie;
use strict;
use utf8;

my $dir = dirname(__FILE__);
my $lib = "$dir/../lib/latexindent.pl";

$ENV{PERL5LIB} = "$lib/perl/lib/perl5";
exec "$lib/latexindent.pl", @ARGV;
croak $ERRNO;
