#!/usr/bin/env -S -- perl -CASD -w

use English;
use File::Basename;
use File::Copy;
use File::Path;
use File::Temp;
use autodie;
use strict;
use utf8;

my $bin   = dirname( $ENV{BIN} );
my $lib   = $ENV{LIB};
my $dir   = dirname(__FILE__);
my @names = qw( perlcritic perltidy );

if ( !-d $lib ) {
  my $tmp = File::Temp->newdir();

  system( 'cpanm', '--local-lib', $tmp, q{--}, 'Perl::Critic' )
    && croak $CHILD_ERROR;

  system( "mv", "--force", "--", $tmp, $lib ) && croak $CHILD_ERROR;
}

foreach my $name (@names) {
  my $src = "$dir/$name.ex.pl";
  my $dst = "$bin/$name";

  if ( $OSNAME eq 'msys' ) {
    $dst = "$dst.pl";
  }

  copy( $src, $dst );
  chmod( 0755, $dst );
}
