#!/usr/bin/env -S -- clojure.sh -M

(import '[java.lang ProcessBuilder ProcessBuilder$Redirect]
        '[java.nio.file Files Paths StandardCopyOption]
        '[java.nio.file.attribute PosixFilePermissions])

(def arch (System/getProperty "os.arch"))
(def os (System/getProperty "os.name"))
(def tmp (-> "TMP"
             (System/getenv)
             (Paths/get (into-array String []))))

(def base "https://github.com/clojure-lsp/clojure-lsp/releases/latest/download/clojure-lsp-native")

(def uri
  (str base "-"
       (case (System/getProperty "os.name")
         "Linux" (str "static-linux-" arch ".zip")
         "Mac OS X" (str "macos-" arch ".zip")
         (str "windows-" arch ".zip"))))

(def bin (let [b (System/getenv "BIN")
               ext (case os
                     "Windows" ".exe"
                     "")]
           (Paths/get (str b ext) (into-array String []))))

(doseq
 [proc (ProcessBuilder/startPipeline
        [(-> (ProcessBuilder. ["get.sh", uri])
             (.redirectError ProcessBuilder$Redirect/INHERIT))
         (->
          (ProcessBuilder. ["unpack.sh", (.toString tmp)])
          (.redirectOutput ProcessBuilder$Redirect/INHERIT)
          (.redirectError ProcessBuilder$Redirect/INHERIT))])]
  (-> proc .waitFor zero? assert))

(Files/move (.resolve tmp "clojure-lsp")
            bin
            (into-array [StandardCopyOption/REPLACE_EXISTING]))

(->> "rwxrwxr-x"
     (PosixFilePermissions/fromString)
     (Files/setPosixFilePermissions bin))
