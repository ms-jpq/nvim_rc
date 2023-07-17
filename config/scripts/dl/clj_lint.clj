#!/usr/bin/env -S -- clojure -M

(import '[java.lang ProcessBuilder ProcessBuilder$Redirect]
        '[java.nio.file Files Paths StandardCopyOption]
        '[java.nio.file.attribute FileAttribute PosixFilePermissions])

(def uri
  (case (System/getProperty "os.name")
    "Linux" "https://github.com/clj-kondo/clj-kondo/releases/latest/download/clj-kondo-2023.07.13-linux-static-amd64.zip"
    "Mac OS X" "https://github.com/clj-kondo/clj-kondo/releases/latest/download/clj-kondo-2023.07.13-macos-aarch64.zip"
    "https://github.com/clj-kondo/clj-kondo/releases/latest/download/clj-kondo-2023.07.13-windows-amd64.zip"))

(def bin (let [b (System/getenv "BIN")
               ext (case (System/getProperty "os.name")
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
           (ProcessBuilder. ["unpack.py", "--dest", (.toString tmp)])
           (.redirectOutput ProcessBuilder$Redirect/INHERIT)
           (.redirectError ProcessBuilder$Redirect/INHERIT))])]
      (assert (== 0 (.waitFor n))))

    (Files/move (.resolve tmp "clj-kondo")
                bin
                (into-array [StandardCopyOption/REPLACE_EXISTING]))

    (finally
      (Files/delete tmp))))

(Files/setPosixFilePermissions
 bin
 (PosixFilePermissions/fromString "rwxrwxr-x"))
