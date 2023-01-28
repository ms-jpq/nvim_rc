#!/usr/bin/env -S -- php
<?php
$argv = [
  "php",
  "{$__DIR__}/../lib/phan/phan.phar",
  "--allow-polyfill-parser",
  "--no-progress-bar",
  "--strict-type-checking",
];

$code = 1;
passthru(join(" ", array_map("escapeshellarg", $argv)), $code);
exit($code);


?>
