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
my $script = "$dir/../exec/latexindent.pl";

if ( !-d $lib ) {
  my $tmp       = File::Temp->newdir();
  my $tmp_lib   = File::Temp->newdir();
  my $perl_libd = "$tmp_lib/_perl_";
  my @perl_libs = qw{YAML::Tiny File::HomeDir Unicode::GCString};

  my $filename = `get -- \Q$uri\E`;
  $CHILD_ERROR && croak $CHILD_ERROR;

  system( 'unpack', '--dest', $tmp, '--', $filename ) && croak $CHILD_ERROR;
  my @globbed = glob("\Q$tmp\E/*");
  move( @globbed, $tmp_lib );

  system( 'cpanm', '--local-lib', $perl_libd, '--', @perl_libs )
    && croak $CHILD_ERROR;

  rmtree($lib);
  move( $tmp_lib, $lib );
}

copy( $script, $bin );
chmod( 0755, $bin );
