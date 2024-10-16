#!/usr/bin/env -S -- php

<?php
$uri = "https://github.com/phan/phan/releases/latest/download/phan.phar";

$lib = getenv("LIB");
$bin = getenv("BIN");
assert($lib && $bin);

$output = [];
$code = -1;
exec(join(" ", array_map("escapeshellarg", ["get.sh", $uri])), $output, $code);
assert($code === 0, join(PHP_EOL, $output));
$file = join(PHP_EOL, $output);

assert(mkdir($lib, 0755, true));

$basename = basename($file);
assert(copy($file, "$lib/$basename"));

if (PHP_OS_FAMILY === "Windows") {
  $bin .= ".php";
}

$dir = dirname(__FILE__);
assert(copy("{$dir}/phan.ex.php", $bin));
assert(chmod($bin, 0755));


?>
