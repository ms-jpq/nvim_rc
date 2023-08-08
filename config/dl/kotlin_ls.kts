#!/usr/bin/env -S -- kotlinc -script
import java.lang.ProcessBuilder.Redirect
import java.nio.file.Path
import kotlin.io.createTempDir
import kotlin.io.path.Path
import kotlin.io.path.createSymbolicLinkPointingTo
import kotlin.io.path.deleteIfExists
import kotlin.io.path.deleteRecursively

val rt = Runtime.getRuntime()
val win = System.getProperty("os.name").startsWith("Windows")

if (win) {
  System.exit(0)
}

val suffix = { path: Path, ext: String ->
  if (win) {
    path.resolveSibling(Path(path.getFileName().toString() + ext))
  } else {
    path
  }
}

val uri = "https://github.com/fwcd/kotlin-language-server/releases/latest/download/server.zip"
val py = System.getenv("PYTHON")!!
val libexec = System.getenv("LIBEXEC")!!
val lib = Path(System.getenv("LIB")!!)
val tmp = Path(createTempDir().getPath())
val ll = suffix(Path(lib.toString(), "bin", "kotlin-language-server"), ".bat")
val bin = suffix(Path(System.getenv("BIN")!!), ".bat")

val procs =
    ProcessBuilder.startPipeline(
        listOf(
            ProcessBuilder(py, Path(libexec, "get.py").toString(), "--", uri)
                .redirectError(Redirect.INHERIT),
            ProcessBuilder(py, Path(libexec, "unpack.py").toString(), "--dst", tmp.toString())
                .redirectOutput(Redirect.INHERIT)
                .redirectError(Redirect.INHERIT)))

for (proc in procs) {
  assert(proc.waitFor() == 0)
}

@OptIn(kotlin.io.path.ExperimentalPathApi::class) lib.deleteRecursively()

val p1 = rt.exec(arrayOf("mv", "-v", "-f", "--", tmp.resolve("server").toString(), lib.toString()))

assert(p1.waitFor() == 0)

val p2 = rt.exec(arrayOf("chmod", "-v", "+x", ll.toString()))

assert(p2.waitFor() == 0)

bin.deleteIfExists()

bin.createSymbolicLinkPointingTo(ll)

@OptIn(kotlin.io.path.ExperimentalPathApi::class) tmp.deleteRecursively()
