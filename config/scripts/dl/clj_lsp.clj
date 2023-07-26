#!/usr/bin/env -S -- clojure -M

(import '[java.lang ProcessBuilder ProcessBuilder$Redirect]
        '[java.nio.file Files Paths StandardCopyOption]
        '[java.nio.file.attribute FileAttribute PosixFilePermissions])

(def os (System/getProperty "os.name"))

(def uri
  (case os
    "Linux" "https://github.com/clojure-lsp/clojure-lsp/releases/latest/download/clojure-lsp-native-linux-amd64.zip"
    "Mac OS X" "https://github.com/clojure-lsp/clojure-lsp/releases/latest/download/clojure-lsp-native-macos-aarch64.zip"
    "https://github.com/clojure-lsp/clojure-lsp/releases/latest/download/clojure-lsp-native-windows-amd64.zip"))

(def bin (let [b (System/getenv "BIN")
               ext (case os
                     "Windows" ".exe"
                     "")]
           (Paths/get (str b ext) (into-array String []))))

(let [tmp (Files/createTempDirectory "" (into-array FileAttribute []))]
  (try
    (doseq
     [n (ProcessBuilder/startPipeline
         [(-> (ProcessBuilder. ["get.py", "--", uri])
              (.redirectError ProcessBuilder$Redirect/INHERIT))
          (->
           (ProcessBuilder. ["unpack.py", "--dst", (.toString tmp)])
           (.redirectOutput ProcessBuilder$Redirect/INHERIT)
           (.redirectError ProcessBuilder$Redirect/INHERIT))])]
      (assert (== 0 (.waitFor n))))

    (Files/move (.resolve tmp "clojure-lsp")
                bin
                (into-array [StandardCopyOption/REPLACE_EXISTING]))

    (finally
      (Files/delete tmp))))

(Files/setPosixFilePermissions
 bin
 (PosixFilePermissions/fromString "rwxrwxr-x"))
