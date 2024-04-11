#!/usr/bin/env -S -- clojure.sh -M

(import '[java.lang ProcessBuilder ProcessBuilder$Redirect]
        '[java.nio.file Files Path StandardCopyOption]
        '[java.nio.file.attribute PosixFilePermissions])
(require
 '[clojure.string :refer [join replace]]
 '[clojure.java.shell :refer [sh]])

(def arch (System/getProperty "os.arch"))
(def tmp (-> "TMP"
             (System/getenv)
             (Path/of (into-array String []))))

(def repo "clj-kondo/clj-kondo")
(def base (str "https://github.com/" repo "/releases/latest/download/clj-kondo"))
(def version
  (let [{:keys [exit err out]} (sh "gh-latest.sh" "." repo)]
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
           (Path/of (str b ext) (into-array String []))))

(doseq
 [proc (ProcessBuilder/startPipeline
        [(-> (ProcessBuilder. ["get.sh", uri])
             (.redirectError ProcessBuilder$Redirect/INHERIT))
         (->
          (ProcessBuilder. ["unpack.sh", (.toString tmp)])
          (.redirectOutput ProcessBuilder$Redirect/INHERIT)
          (.redirectError ProcessBuilder$Redirect/INHERIT))])]
  (-> proc .waitFor zero? assert))

(Files/move (.resolve tmp "clj-kondo")
            bin
            (into-array [StandardCopyOption/REPLACE_EXISTING]))

(->> "rwxrwxr-x"
     (PosixFilePermissions/fromString)
     (Files/setPosixFilePermissions bin))
