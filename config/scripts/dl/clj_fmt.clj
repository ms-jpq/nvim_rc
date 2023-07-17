#!/usr/bin/env -S -- clojure -M

(import '[java.lang ProcessBuilder ProcessBuilder$Redirect]
        '[java.nio.file Files Paths StandardCopyOption]
        '[java.nio.file.attribute FileAttribute])

(def uri
  (case (System/getProperty "os.name")
    "Linux" "https://github.com/weavejester/cljfmt/releases/latest/download/cljfmt-0.10.6-linux-amd64-static.tar.gz"
    "Mac OS X" "https://github.com/weavejester/cljfmt/releases/latest/download/cljfmt-0.10.6-darwin-aarch64.tar.gz"
    "https://github.com/weavejester/cljfmt/releases/latest/download/cljfmt-0.10.6-win-amd64.zip"))

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

    (Files/move (.resolve tmp "cljfmt")
                bin
                (into-array [StandardCopyOption/REPLACE_EXISTING]))

    (finally
      (Files/delete tmp))))
