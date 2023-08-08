#!/usr/bin/env -S -- runhaskell

import           Control.Arrow      ((>>>))
import           Data.Functor       ((<&>))
import           System.Directory   (copyFileWithMetadata, getCurrentDirectory,
                                     removePathForcibly, renameDirectory)
import           System.Environment (getEnv)
import           System.Exit        (exitSuccess)
import           System.FilePath    (takeDirectory, (</>))
import           System.Info        (os)
import           System.Process     (callProcess, readProcess)
import           Text.Printf        (printf)

repo = "haskell/haskell-language-server"
base = "https://github.com/haskell/haskell-language-server/releases/latest/download/haskell-language-server"

uri "darwin" = printf "%s-%s-aarch64-apple-darwin.tar.xz" base
uri "linux"  = printf "%s-%s-x86_64-linux-ubuntu22.04.tar.xz" base
uri "nt"     = printf "%s-%s-x86_64-mingw64.zip" base

suffix "nt" = ".exe"
suffix _    = ""

run "nt" = exitSuccess
run os = do
  lib <- getEnv "LIB"
  cwd <- getCurrentDirectory <&> (takeDirectory >>> takeDirectory)
  tmp <- readProcess "mktemp" ["-d"] ""
  version <- readProcess "gh-latest.sh" [repo] ""

  let tramp = cwd </> "config" </> "dl" </> "hls.ex.sh"
  let srv = tmp </> printf "haskell-language-server-%s" version
  let link = uri os version

  _ <- readProcess "get.py" ["--", link] ""
    >>= readProcess "unpack.py" ["--dst", tmp]
    >>= putStr

  _ <- removePathForcibly lib
  _ <- renameDirectory srv lib
  _ <- getEnv "BIN" >>= copyFileWithMetadata tramp
  _ <- removePathForcibly tmp
  exitSuccess

main = run os
