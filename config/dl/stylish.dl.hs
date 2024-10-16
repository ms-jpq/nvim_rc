#!/usr/bin/env -S -- runhaskell

import           Data.Function      ((&))
import           System.Directory   (getPermissions, renameFile,
                                     setOwnerExecutable, setPermissions)
import           System.Environment (getEnv, getExecutablePath)
import           System.Exit        (exitSuccess)
import           System.FilePath    (dropExtension, takeBaseName, (</>))
import           System.Info        (os)
import           System.Process     (readProcess)
import           Text.Printf        (printf)


repo = "haskell/stylish-haskell"
base = "https://github.com/haskell/stylish-haskell/releases/latest/download/stylish-haskell"

uri "darwin" = printf "%s-%s-darwin-x86_64.zip" base
uri "linux"  = printf "%s-%s-linux-x86_64.tar.gz" base

nameof "linux" = dropExtension
nameof _       = id

run "mingw32" = exitSuccess
run os = do
  tmp <- getEnv "TMP"
  version <- readProcess "env" ["--", "gh-latest.sh", ".", repo] ""

  let link = uri os version
  let name = nameof os link & takeBaseName
  let srv = tmp </> name </> "stylish-haskell"

  _ <- readProcess "env" ["--", "get.sh", link] ""
    >>= readProcess "env" ["--", "unpack.sh", tmp]
    >>= putStr

  _ <- getExecutablePath >>= getPermissions >>= setPermissions srv
  _ <- getEnv "BIN" >>= renameFile srv
  exitSuccess

main = run os
