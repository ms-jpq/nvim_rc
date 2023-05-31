#!/usr/bin/env -S -- clojure -M

(import '[java.lang ProcessBuilder ProcessBuilder$Redirect]
        '[java.nio.file Files Paths StandardCopyOption]
        '[java.nio.file.attribute FileAttribute PosixFilePermissions])

(def os (System/getProperty "os.name"))

(def bin (let [b (System/getenv "BIN")
               ext (case os
                     "Windows" ".exe"
                     "")]
           (Paths/get (str b ext) (into-array String []))))

(def uri (System/getenv
          (case os
            "Linux" "LINUX_URI"
            "Mac OS X" "DARWIN_URI"
            "NT_URI")))

(let [tmp (Files/createTempDirectory "" (into-array FileAttribute []))]
  (try
    (doseq
     [n (ProcessBuilder/startPipeline
         [(-> (ProcessBuilder. ["get", "--", uri])
              (.redirectError ProcessBuilder$Redirect/INHERIT))
          (->
           (ProcessBuilder. ["unpack", "--dest", (.toString tmp)])
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
