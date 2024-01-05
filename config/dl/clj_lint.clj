#!/usr/bin/env -S -- clojure.sh -M

(import '[java.lang ProcessBuilder ProcessBuilder$Redirect]
        '[java.nio.file Files Paths StandardCopyOption]
        '[java.nio.file.attribute FileAttribute PosixFilePermissions])
(require
 '[clojure.string :refer [join replace]]
 '[clojure.java.shell :refer [sh]])

(def arch (System/getProperty "os.arch"))
(def repo "clj-kondo/clj-kondo")
(def base (str "https://github.com/" repo "/releases/latest/download/clj-kondo"))
(def version
  (let [{:keys [exit err out]} (sh "gh-latest.sh" repo)]
    (print err)
    (assert (zero? exit))
    (replace out #"^v" "")))

(def uri
  (join "-" [base version
             (case (System/getProperty "os.name")
               "Linux" (str "linux-static-" arch ".zip")
               "Mac OS X" (str "macos-" arch ".zip")
               (str "windows-" arch ".zip"))]))

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

    (Files/move (.resolve tmp "clj-kondo")
                bin
                (into-array [StandardCopyOption/REPLACE_EXISTING]))

    (finally
      (Files/delete tmp))))

(Files/setPosixFilePermissions
 bin
 (PosixFilePermissions/fromString "rwxrwxr-x"))
