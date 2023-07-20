#!/usr/bin/env -S -- php

<?php
$uri = "https://github.com/phpactor/phpactor/releases/latest/download/phpactor.phar";

$output = [];
$code = -1;
exec(
  join(" ", array_map("escapeshellarg", ["get.py", "--", $uri])),
  $output,
  $code
);
assert($code === 0, join(PHP_EOL, $output));
$file = join(PHP_EOL, $output);

$bin = getenv("BIN");
assert($bin);

copy($file, $bin);
chmod($bin, 0755);


?>
