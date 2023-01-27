#!/usr/bin/env -S -- perl

use English;
use File::Basename;
use File::Copy;
use File::Path;
use File::Temp;
use autodie;
use diagnostics;
use strict;
use utf8;
use warnings;

my $bin     = dirname( $ENV{BIN} );
my $lib     = $ENV{LIB};
my $uri     = $ENV{URI};
my $dir     = dirname(__FILE__);
my $scripts = "$dir/../exec";
my @names   = qw( perlcritic perltidy );

if ( !-d $lib ) {
  my $tmp = File::Temp->newdir();

  system( 'cpanm', '--local-lib', $tmp, q{--}, 'Perl::Critic' )
    && croak $CHILD_ERROR;

  rmtree($lib);
  move( $tmp, $lib );
}

foreach my $name (@names) {
  my $src = "$scripts/$name.pl";
  my $dst = "$bin/$name";

  copy( $src, $dst );
  chmod 0755, $dst;
}
