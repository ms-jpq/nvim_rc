#!/usr/bin/env -S -- perl -CASD

use English;
use File::Basename;
use autodie;
use strict;
use utf8;

my $dir = dirname(__FILE__);
my $lib = "$dir/../lib/perlcritic";

$ENV{PERL5LIB} = "$lib/lib/perl5";
exec "$lib/bin/perltidy", @ARGV;
croak $ERRNO;
