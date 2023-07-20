#!/usr/bin/env -S -- runhaskell

import           System.Directory      (copyFileWithMetadata, getPermissions,
                                        setOwnerExecutable, setPermissions)
import           System.Environment    (getEnv, getExecutablePath)
import           System.FilePath       ((</>))
import           System.FilePath.Posix (dropExtension, takeBaseName)
import           System.Info           (os)
import           System.Process        (callProcess, readProcess)
import           Text.Printf           (printf)

version = "v0.14.5.0"
base = "https://github.com/haskell/stylish-haskell/releases/latest/download/stylish-haskell"

uri "darwin" = printf "%s-%s-darwin-x86_64.zip"     base
uri "linux"  = printf "%s-%s-linux-x86_64.tar.gz" base

nameof "linux" = dropExtension
nameof _       = id

main = do
  tmp <- readProcess "mktemp" ["-d"] ""

  let link = uri os version
  let name = nameof os link
  let srv = tmp </> (takeBaseName name) </> "stylish-haskell"

  _ <- readProcess "get.py" ["--", link] ""
    >>= readProcess "unpack.py" ["--dst", tmp]
    >>= putStr

  _ <- getExecutablePath >>= getPermissions >>= setPermissions srv
  _ <- getEnv "BIN" >>= copyFileWithMetadata srv
  pure ()
