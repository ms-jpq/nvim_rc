#!/usr/bin/env -S php
<?php
$uri = getenv("URI");
assert($uri);

$output = [];
$code = -1;
exec(
  join(" ", array_map("escapeshellarg", ["get", "--", $uri])),
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

$d = __DIR__;
$bin = getenv("BIN");
assert($bin);
copy("$d/../exec/phan.sh", $bin);
chmod($bin, 0755);


?>
