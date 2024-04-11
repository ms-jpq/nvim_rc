#!/usr/bin/env -S -- runhaskell

import           Control.Arrow      ((>>>))
import           Data.Function      ((&))
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
uri "linux"   = printf "%s-%s-x86_64-linux-unknown.tar.xz" base
uri "mingw32" = printf "%s-%s-x86_64-mingw64.zip" base

suffix "mingw32" = flip addExtension ".sh"
suffix _         = id

contents "mingw32" _ tmp = tmp
contents _ version tmp   = tmp </> printf "haskell-language-server-%s" version

run os = do
  lib <- getEnv "LIB"
  tmp <- getEnv "TMP"
  cwd <- getCurrentDirectory <&> (takeDirectory >>> takeDirectory)
  version <- readProcess "env" ["--", "gh-latest.sh", ".", repo] ""

  let tramp = cwd </> "config" </> "dl" </> "hls.ex.sh"
  let link = uri os version

  _ <- readProcess "env" ["--", "get.sh", link] ""
    >>= readProcess "env" ["--", "unpack.sh", tmp]
    >>= putStr

  _ <- removePathForcibly lib
  _ <- contents os version tmp & flip renameDirectory lib
  _ <- getEnv "BIN" <&> suffix os >>= copyFileWithMetadata tramp
  exitSuccess

main = run os
