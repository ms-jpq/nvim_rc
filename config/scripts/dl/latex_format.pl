#!/usr/bin/env -S -- perl

use File::Basename;
use File::Copy;
use File::Path;
use File::Temp;
use autodie;
use diagnostics;
use strict;
use utf8;
use warnings;

my $bin = $ENV{BIN};
my $lib = $ENV{LIB};
my $uri = $ENV{URI};

if ( !-d $lib ) {
  my $tmp       = File::Temp->newdir();
  my $tmp_lib   = File::Temp->newdir();
  my $perl_libd = "$tmp_lib/_perl_";
  my @perl_libs = ( 'YAML::Tiny', 'File::HomeDir', 'Unicode::GCString' );
  my $dir       = dirname(__FILE__);
  my $script    = "$dir/../exec/latexindent.sh";

  my $filename = `get -- \Q$uri\E`;
  $? && die $?;

  system( 'unpack', '--dest', $tmp, '--', $filename ) && die $?;
  my @globbed = glob("\Q$tmp\E/*");
  move( @globbed, $tmp_lib );

  system( 'cpanm', '--local-lib', $perl_libd, '--', @perl_libs )
    && die $?;

  rmtree($lib);
  move( $tmp_lib, $lib );
  copy( $script, $bin );
  chmod( 0755, $bin );
}
