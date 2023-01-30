#!/usr/bin/env -S -- php
<?php
$prefix = [
  "php",
  "{$__DIR__}/../lib/phan/phan.phar",
  "--allow-polyfill-parser",
  "--no-progress-bar",
  "--strict-type-checking",
];
$args = array_map(
  "escapeshellarg",
  array_merge($prefix, array_slice($argv, 1))
);

$code = 1;
passthru(join(" ", $args), $code);
exit($code);


?>
