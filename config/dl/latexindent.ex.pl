#!/usr/bin/env -S -- PERL_UNICODE=CASD perl -w

use Carp;
use English;
use File::Basename;
use File::Spec::Functions;
use autodie;
use strict;
use utf8;

my $dir = dirname(__FILE__);
my $lib = catfile( $dir, '..', 'lib', 'latexindent.pl' );

$ENV{PERL5LIB} = catfile( $lib, 'perl', 'lib', 'perl5' );
exec 'perl', catfile( $lib, 'lib', 'latexindent.pl' ), @ARGV;
croak $ERRNO;
