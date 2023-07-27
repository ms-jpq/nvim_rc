#!/usr/bin/env -S -- runhaskell

import           Data.Function         ((&))
import           System.Directory      (copyFileWithMetadata, getPermissions,
                                        removePathForcibly, setOwnerExecutable, setPermissions)
import           System.Environment    (getEnv, getExecutablePath)
import           System.FilePath       ((</>))
import           System.FilePath.Posix (dropExtension, takeBaseName)
import           System.Info           (os)
import           System.Process        (callProcess, readProcess)
import           Text.Printf           (printf)

repo = "haskell/stylish-haskell"
base = printf "https://github.com/%s/releases/latest/download/stylish-haskell" repo

uri "darwin" = printf "%s-%s-darwin-x86_64.zip" base
uri "linux"  = printf "%s-%s-linux-x86_64.tar.gz" base

nameof "linux" = dropExtension
nameof _       = id

main = do
  tmp <- readProcess "mktemp" ["-d"] ""
  version <- readProcess "gh-latest.sh" [repo] ""

  let link = uri os version
  let name = nameof os link & takeBaseName
  let srv = tmp </> name </> "stylish-haskell"

  _ <- readProcess "get.py" ["--", link] ""
    >>= readProcess "unpack.py" ["--dst", tmp]
    >>= putStr

  _ <- getExecutablePath >>= getPermissions >>= setPermissions srv
  _ <- getEnv "BIN" >>= copyFileWithMetadata srv
  _ <- removePathForcibly tmp
  pure ()