#!/usr/bin/env -S -- perl -CASD -w

use English;
use File::Basename;
use File::Copy;
use File::Path;
use File::Spec::Functions;
use File::Temp;
use autodie;
use strict;
use utf8;

my $dir    = dirname(__FILE__);
my $cpan   = catfile( dirname( $Config{perlpath} ), 'cpan' );
my $bin    = $ENV{BIN};
my $lib    = $ENV{LIB};
my $script = catfile( $dir, 'latexindent.ex.pl' );

if ( !-d $lib ) {
  my $tmp       = File::Temp->newdir();
  my $tmp_lib   = File::Temp->newdir();
  my $perl_libd = "$tmp_lib/perl";
  my @perl_libs = qw{YAML::Tiny File::HomeDir Unicode::GCString};

  $ENV{HOME}                = $perl_libd;
  $ENV{PERL_LOCAL_LIB_ROOT} = $perl_libd;
  $ENV{PERL_MB_OPT}         = "--install_base $perl_libd";
  $ENV{PERL_MM_OPT}         = "INSTALL_BASE=$perl_libd";
  $ENV{PERL5LIB}            = catfile( $perl_libd, 'lib', 'perl5' );

  my $repo = 'cmhughes/latexindent.pl';
  my $tag  = `gh-latest.sh \Q$repo\E`;
  $CHILD_ERROR && croak $CHILD_ERROR;

  my $uri      = "https://github.com/$repo/archive/refs/tags/$tag.tar.gz";
  my $filename = `get.py -- \Q$uri\E`;
  $CHILD_ERROR && croak $CHILD_ERROR;

  system( 'unpack.py', '--dst', $tmp, q{--}, $filename ) && croak $CHILD_ERROR;
  my @globbed = glob "\Q$tmp\E/*";
  move( @globbed, $tmp_lib );

  system( $cpan, '-T', '-I', '-i', @perl_libs )
    && croak $CHILD_ERROR;

  system( 'mv', '-v', '-f', q{--}, $tmp_lib, $lib ) && croak $CHILD_ERROR;

  rmtree($tmp);
}

copy( $script, $bin );
chmod 0755, $bin;
