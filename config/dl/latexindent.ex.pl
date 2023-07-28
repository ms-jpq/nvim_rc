#!/usr/bin/env -S -- perl -CASD -w

use English;
use File::Basename;
use autodie;
use strict;
use utf8;

my $dir = dirname(__FILE__);
my $lib = "$dir/../lib/latexindent";

$ENV{PERL5LIB} = "$lib/_perl_/lib/perl5";
exec( "$lib/latexindent.pl", @ARGV );
croak;
