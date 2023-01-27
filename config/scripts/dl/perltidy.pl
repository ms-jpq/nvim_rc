#!/usr/bin/env -S -- perl

use File::Basename;
use File::Copy;
use File::Path;
use File::Temp;
use English;
use autodie;
use diagnostics;
use strict;
use utf8;
use warnings;

my $bin    = $ENV{BIN};
my $lib    = $ENV{LIB};
my $uri    = $ENV{URI};
my $dir    = dirname(__FILE__);
my $script = "$dir/../exec/perltidy.pl";

if ( !-d $lib ) {
  my $tmp = File::Temp->newdir();

  system( 'cpanm', '--local-lib', $tmp, '--', 'Perl::Tidy' )
    && croak $CHILD_ERROR;

  rmtree($lib);
  move( $tmp, $lib );
}

copy( $script, $bin );
chmod( 0755, $bin );
