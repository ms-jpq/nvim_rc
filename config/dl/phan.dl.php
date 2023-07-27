#!/usr/bin/env -S -- php

<?php
$uri = "https://github.com/phan/phan/releases/latest/download/phan.phar";

$output = [];
$code = -1;
exec(
  join(" ", array_map("escapeshellarg", ["get.py", "--", $uri])),
  $output,
  $code
);
assert($code === 0, join(PHP_EOL, $output));
$file = join(PHP_EOL, $output);

$lib = getenv("LIB");
assert($lib);
mkdir($lib, 0755, true);

$basename = basename($file);
copy($file, "$lib/$basename");

$bin = getenv("BIN");
assert($bin);
if (PHP_OS_FAMILY === "Windows") {
  $bin .= ".php";
}

copy("{$__DIR__}/../exec/phan.php", $bin);

?>
