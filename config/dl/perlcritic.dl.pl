#!/usr/bin/env -S -- perl -CASD -w

use Config;
use English;
use File::Basename;
use File::Copy;
use File::Path;
use File::Spec::Functions;
use File::Temp;
use autodie;
use strict;
use utf8;

my $dir   = dirname(__FILE__);
my $cpan  = catfile( dirname( $Config{perlpath} ), 'cpan' );
my $bin   = dirname( $ENV{BIN} );
my $lib   = $ENV{LIB};
my @names = qw( perlcritic perltidy );

if ( $OSNAME eq 'MSWin32' ) {
  $cpan = '$cpan.bat';
}

if ( !-x $cpan ) {
  exit;
}

if ( !-d $lib ) {
  my $tmp = File::Temp->newdir();

  $ENV{HOME}                = $tmp;
  $ENV{PERL_LOCAL_LIB_ROOT} = $tmp;
  $ENV{PERL_MB_OPT}         = "--install_base $tmp";
  $ENV{PERL_MM_OPT}         = "INSTALL_BASE=$tmp";
  $ENV{PERL5LIB}            = catfile( $tmp, 'lib', 'perl5' );

  system( $cpan, '-T', '-I', '-i', 'Perl::Critic' )
    && croak $CHILD_ERROR;

  system( "mv", "--", $tmp, $lib ) && croak $CHILD_ERROR;
}

foreach my $name (@names) {
  my $src = catfile( $dir, "$name.ex.pl" );
  my $dst = catfile( $bin, "$name.pl" );

  copy( $src, $dst );
  chmod( 0755, $dst );
}
