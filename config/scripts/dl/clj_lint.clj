#!/usr/bin/env -S -- clojure -M

(import '[java.lang ProcessBuilder ProcessBuilder$Redirect]
        '[java.nio.file Files Paths StandardCopyOption]
        '[java.nio.file.attribute FileAttribute PosixFilePermissions])

(def bin (let [b (System/getenv "BIN")
               ext (case (System/getProperty "os.name")
                     "Windows" ".exe"
                     "")]
           (Paths/get (str b ext) (into-array String []))))

(def uri (System/getenv
          (case (System/getProperty "os.name")
            "Linux" "LINUX_URI"
            "Darwin" "DARWIN_URI"
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

    (Files/move (.resolve tmp "clj-kondo")
                bin
                (into-array [StandardCopyOption/REPLACE_EXISTING]))

    (finally
      (Files/delete tmp))))

(Files/setPosixFilePermissions
 bin
 (PosixFilePermissions/fromString "rwxrwxr-x"))
