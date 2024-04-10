#!/usr/bin/env -S -- kotlinc -script
import java.lang.ProcessBuilder.Redirect
import java.nio.file.Path
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
val tmp = Path(System.getenv("TMP")!!)
val lib = Path(System.getenv("LIB")!!)
val ll = suffix(Path(lib.toString(), "bin", "kotlin-language-server"), ".bat")
val bin = suffix(Path(System.getenv("BIN")!!), ".bat")

val procs =
    ProcessBuilder.startPipeline(
        listOf(
            ProcessBuilder("env", "--", "get.sh", uri).redirectError(Redirect.INHERIT),
            ProcessBuilder("env", "--", "unpack.sh", tmp.toString())
                .redirectOutput(Redirect.INHERIT)
                .redirectError(Redirect.INHERIT)))

for (proc in procs) {
  assert(proc.waitFor() == 0)
  assert(!proc.isAlive())
}

@OptIn(kotlin.io.path.ExperimentalPathApi::class) lib.deleteRecursively()

tmp.resolve("server").toFile().copyRecursively(lib.toFile())

ll.toFile().setExecutable(true)

bin.deleteIfExists()

bin.createSymbolicLinkPointingTo(ll)
