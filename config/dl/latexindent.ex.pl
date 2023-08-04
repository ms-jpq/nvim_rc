#!/usr/bin/env -S -- perl -CASD

use English;
use File::Basename;
use File::Spec::Functions;
use autodie;
use strict;
use utf8;

my $dir = dirname(__FILE__);
my $lib = catfile( $dir, '..', 'lib', 'latexindent.pl' );

$ENV{PERL5LIB} = catfile( $lib, 'perl', 'lib', 'perl5' );
exec catfile( $lib, 'latexindent.pl' ), @ARGV;
croak $ERRNO;
