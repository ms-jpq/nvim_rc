#!/usr/bin/env -S -- clojure.sh -M

(import '[java.lang ProcessBuilder ProcessBuilder$Redirect]
        '[java.nio.file Files Paths StandardCopyOption]
        '[java.nio.file.attribute FileAttribute])
(require
 '[clojure.string :refer [join]]
 '[clojure.java.shell :refer [sh]])

(def arch (System/getProperty "os.arch"))
(def repo "weavejester/cljfmt")
(def base (str "https://github.com/" repo "/releases/latest/download/cljfmt"))
(def version
  (let [{:keys [exit err out]} (sh "gh-latest.sh" repo)]
    (print err)
    (assert (zero? exit))
    out))

(def uri
  (join "-" [base version
             (case (System/getProperty "os.name")
               "Linux" (str "linux-" arch "-static.tar.gz")
               "Mac OS X" (str "darwin-" arch ".tar.gz")
               (str "win-" arch ".zip"))]))

(def bin (let [b (System/getenv "BIN")
               ext (case (System/getProperty "os.name")
                     "Windows" ".exe"
                     "")]
           (Paths/get (str b ext) (into-array String []))))

(let [tmp (Files/createTempDirectory "" (into-array FileAttribute []))]
  (try
    (doseq
     [proc (ProcessBuilder/startPipeline
            [(-> (ProcessBuilder. ["get.py", "--", uri])
                 (.redirectError ProcessBuilder$Redirect/INHERIT))
             (->
              (ProcessBuilder. ["unpack.py", "--dst", (.toString tmp)])
              (.redirectOutput ProcessBuilder$Redirect/INHERIT)
              (.redirectError ProcessBuilder$Redirect/INHERIT))])]
      (-> proc .waitFor zero? assert))

    (Files/move (.resolve tmp "cljfmt")
                bin
                (into-array [StandardCopyOption/REPLACE_EXISTING]))

    (finally
      (Files/delete tmp))))
