#!/usr/bin/env -S -- php

<?php
$uri =
  "https://github.com/phpactor/phpactor/releases/latest/download/phpactor.phar";

$bin = getenv("BIN");
assert($bin);

$output = [];
$code = -1;
exec(join(" ", array_map("escapeshellarg", ["get.sh", $uri])), $output, $code);
assert($code === 0, join(PHP_EOL, $output));
$file = join(PHP_EOL, $output);

assert(copy($file, $bin));
assert(chmod($bin, 0755));


?>
