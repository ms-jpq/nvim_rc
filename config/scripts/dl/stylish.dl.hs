#!/usr/bin/env -S -- runhaskell

import           System.Environment    (getEnv)
import           System.FilePath       ((</>))
import           System.FilePath.Posix (takeBaseName)
import           System.Info           (os)
import           System.Process        (callProcess, readProcess)
import           Text.Printf           (printf)

version = "v0.14.5.0"
base = "https://github.com/haskell/stylish-haskell/releases/latest/download/stylish-haskell"

uri "darwin" = printf "%s-%s-darwin-x86_64.zip"     base
uri "linux"  = printf "%s-%s-linux-x86_64.tar.gz" base
link = uri os version

main = do
  bin <- getEnv "BIN"
  tmp <- readProcess "mktemp" ["-d"] ""
  let srv = tmp </> (takeBaseName link) </> "stylish-haskell"
  tz <- readProcess "get.py" ["--", link] ""
  out <- readProcess "unpack.py" ["--dst", tmp] tz
  putStr out
  _ <- callProcess "install" ["-b", "--", srv, bin]
  pure ()
