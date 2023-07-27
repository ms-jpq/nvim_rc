#!/usr/bin/env -S -- runhaskell

import           Data.Functor       ((<&>))
import           System.Directory   (copyFileWithMetadata, getCurrentDirectory,
                                     removePathForcibly, renameDirectory)
import           System.Environment (getEnv)
import           System.FilePath    (takeDirectory, (</>))
import           System.Info        (os)
import           System.Process     (callProcess, readProcess)
import           Text.Printf        (printf)

version = "2.0.0.1"
base = "https://github.com/haskell/haskell-language-server/releases/latest/download/haskell-language-server"

uri "darwin" = printf "%s-%s-aarch64-apple-darwin.tar.xz" base
uri "linux"  = printf "%s-%s-x86_64-linux-ubuntu22.04.tar.xz" base
uri "nt"     = printf "%s-%s-x86_64-mingw64.zip" base

suffix "nt" = ".exe"
suffix _    = ""

main = do
  lib <- getEnv "LIB"
  cwd <- getCurrentDirectory <&> takeDirectory
  tmp <- readProcess "mktemp" ["-d"] ""

  let tramp = cwd </> "config" </> "scripts" </> "dl" </> "hls.ex.sh"
  let srv = tmp </> printf "haskell-language-server-%s" version
  let link = uri os version

  _ <- readProcess "get.py" ["--", link] ""
    >>= readProcess "unpack.py" ["--dst", tmp]
    >>= putStr

  _ <- removePathForcibly lib
  _ <- renameDirectory srv lib
  _ <- getEnv "BIN" >>= copyFileWithMetadata tramp
  pure ()
