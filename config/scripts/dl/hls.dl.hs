#!/usr/bin/env -S -- runhaskell

import           System.Directory   (copyFileWithMetadata, getCurrentDirectory,
                                     removePathForcibly, renameDirectory)
import           System.Environment (getEnv)
import           System.FilePath    (takeDirectory, (</>))
import           System.Info        (os)
import           System.Process     (callProcess, readProcess)
import           Text.Printf        (printf)

version = "2.0.0.1"
base = "https://github.com/haskell/haskell-language-server/releases/latest/download/haskell-language-server"

uri "darwin" = printf "%s-%s-aarch64-apple-darwin.tar.xz"     base
uri "linux"  = printf "%s-%s-x86_64-linux-ubuntu22.04.tar.xz" base
uri "nt"     = printf "%s-%s-x86_64-mingw64.zip"              base
link = uri os version

suffix "nt" = ".exe"
suffix _    = ""

main = do
  lib <- getEnv "LIB"
  bin <- getEnv "BIN"
  cwd <- getCurrentDirectory
  let tramp = (takeDirectory . takeDirectory) cwd </> "config" </> "scripts" </> "dl" </> "hls.ex.sh"
  tmp <- readProcess "mktemp" ["-d"] ""
  let srv = tmp </> (printf "haskell-language-server-%s" version)
  tz <- readProcess "get.py" ["--", link] ""
  out <- readProcess "unpack.py" ["--dst", tmp] tz
  putStr out
  _ <- removePathForcibly lib
  _ <- renameDirectory srv lib
  _ <- copyFileWithMetadata tramp bin
  pure ()
