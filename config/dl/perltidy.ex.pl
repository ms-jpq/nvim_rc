#!/usr/bin/env -S -- PERL_UNICODE=ASD perl -w

use Carp;
use English;
use File::Basename;
use File::Spec::Functions;
use autodie;
use strict;
use utf8;

my $dir = dirname(__FILE__);
my $lib = catfile( $dir, '..', 'lib', 'perlcritic.pl' );

$ENV{PERL5LIB} = catfile( $lib, 'lib', 'perl5' );
exec 'perl', catfile( $lib, 'bin', 'perltidy' ), @ARGV;
croak $ERRNO;
