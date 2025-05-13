#!/usr/bin/env -S -- php
<?php
declare(strict_types=1);

$bin = getenv("BIN");
$lib = getenv("LIB");
assert($bin && $lib);

mkdir($lib, 0755, true);

$output = [];
$code = -1;
exec(
  join(
    " ",
    array_map("escapeshellarg", [
      "composer",
      "--no-interaction",
      "--no-plugins",
      "--working-dir",
      $lib,
      "require",
      "--update-no-dev",
      "--",
      "phan/phan",
    ])
  ),
  $output,
  $code
);
assert($code === 0, join(PHP_EOL, $output));

if (file_exists($bin)) {
  unlink($bin);
}
assert(symlink(join("/", [$lib, "vendor", "bin", "phan"]), $bin));


?>
