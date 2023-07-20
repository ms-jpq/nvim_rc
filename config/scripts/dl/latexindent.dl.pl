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

my $bin    = $ENV{BIN};
my $lib    = $ENV{LIB};
my $dir    = dirname(__FILE__);
my $script = "$dir/latexindent.ex.pl";

if ( $OSNAME eq 'msys' ) {
  $bin = "$bin.pl";
}

if ( !-d $lib ) {
  my $tmp       = File::Temp->newdir();
  my $tmp_lib   = File::Temp->newdir();
  my $perl_libd = "$tmp_lib/_perl_";
  my @perl_libs = qw{YAML::Tiny File::HomeDir Unicode::GCString};

  my $tags = 'https://api.github.com/repos/cmhughes/latexindent.pl/tags';
  my $json =
    `curl --fail --location --no-progress-meter --max-time 60 -- \Q$tags\E`;
  $CHILD_ERROR && croak $CHILD_ERROR;

  my $jq = '$json[0].name';
  my $tag =
`jq --exit-status --null-input --raw-output \Q$jq\E --argjson json \Q$json\E`;
  $CHILD_ERROR && croak $CHILD_ERROR;

  my $uri =
    "https://github.com/cmhughes/latexindent.pl/archive/refs/tags/$tag.tar.gz";
  my $filename = `get.py -- \Q$uri\E`;
  $CHILD_ERROR && croak $CHILD_ERROR;

  system( 'unpack.py', '--dst', $tmp, q{--}, $filename ) && croak $CHILD_ERROR;
  my @globbed = glob "\Q$tmp\E/*";
  move( @globbed, $tmp_lib );

  system( 'cpanm', '--local-lib', $perl_libd, q{--}, @perl_libs )
    && croak $CHILD_ERROR;

  system( 'mv', '--force', '--', $tmp_lib, $lib ) && croak $CHILD_ERROR;
}

copy( $script, $bin );
chmod( 0755, $bin );
