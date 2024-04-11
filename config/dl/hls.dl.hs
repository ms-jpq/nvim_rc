#!/usr/bin/env -S -- runhaskell

import           Control.Arrow      ((>>>))
import           Data.Functor       ((<&>))
import           System.Directory   (copyFileWithMetadata, getCurrentDirectory,
                                     removePathForcibly, renameDirectory)
import           System.Environment (getEnv)
import           System.Exit        (exitSuccess)
import           System.FilePath    (addExtension, takeDirectory, (</>))
import           System.Info        (os)
import           System.Process     (readProcess)
import           Text.Printf        (printf)

repo = "haskell/haskell-language-server"
base = "https://github.com/haskell/haskell-language-server/releases/latest/download/haskell-language-server"

uri "darwin"  = printf "%s-%s-aarch64-apple-darwin.tar.xz" base
uri "linux"   = printf "%s-%s-x86_64-linux-ubuntu22.04.tar.xz" base
uri "mingw32" = printf "%s-%s-x86_64-mingw64.zip" base

suffix "mingw32" = flip addExtension ".sh"
suffix _         = id

run os = do
  lib <- getEnv "LIB"
  tmp <- getEnv "TMP"
  cwd <- getCurrentDirectory <&> (takeDirectory >>> takeDirectory)
  version <- readProcess "gh-latest.sh" [".", repo] ""

  let tramp = cwd </> "config" </> "dl" </> "hls.ex.sh"
  let srv = tmp </> printf "haskell-language-server-%s" version
  let link = uri os version

  _ <- readProcess "get.sh" [link] ""
    >>= readProcess "unpack.sh" [tmp]
    >>= putStr

  _ <- removePathForcibly lib
  _ <- readProcess "mv" ["-v", "-f", "--", srv, lib] ""
  _ <- getEnv "BIN" <&> suffix os >>= copyFileWithMetadata tramp
  _ <- removePathForcibly tmp
  exitSuccess

main = run os
