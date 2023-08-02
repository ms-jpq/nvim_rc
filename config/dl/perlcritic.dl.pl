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

  $ENV{HOME}                = $tmp;
  $ENV{PERL_LOCAL_LIB_ROOT} = $tmp;
  $ENV{PERL_MB_OPT}         = "--install_base $tmp";
  $ENV{PERL_MM_OPT}         = "INSTALL_BASE=$tmp";
  $ENV{PERL5LIB}            = "$tmp/lib/perl5";

  system( 'cpan', '-T', '-I', '-i', 'Perl::Critic' )
    && croak $CHILD_ERROR;

  system( 'mv', '-v', '-f', q{--}, $tmp, $lib ) && croak $CHILD_ERROR;
}

foreach my $name (@names) {
  my $src = "$dir/$name.ex.pl";
  my $dst = "$bin/$name.pl";

  copy( $src, $dst );
  chmod( 0755, $dst );
}
