#!/usr/bin/env -S -- kotlinc -script
import java.lang.ProcessBuilder.Redirect
import java.nio.file.attribute.PosixFilePermission
import kotlin.io.createTempDir
import kotlin.io.path.Path
import kotlin.io.path.createSymbolicLinkPointingTo
import kotlin.io.path.deleteIfExists
import kotlin.io.path.deleteRecursively
import kotlin.io.path.moveTo
import kotlin.io.path.setPosixFilePermissions

val lib = Path(System.getenv("LIB")!!)
val ll = Path(lib.toString(), "bin", "kotlin-language-server")
val bin = Path(System.getenv("BIN")!!)
val tmp = Path(createTempDir().getPath())

val procs =
    ProcessBuilder.startPipeline(
        listOf(
            ProcessBuilder("get", "--", System.getenv("URI")!!).redirectError(Redirect.INHERIT),
            ProcessBuilder("unpack", "--dest", tmp.toString())
                .redirectOutput(Redirect.INHERIT)
                .redirectError(Redirect.INHERIT)))

for (proc in procs) {
  assert(proc.waitFor() == 0)
}

@OptIn(kotlin.io.path.ExperimentalPathApi::class) lib.deleteRecursively()

tmp.resolve("server").moveTo(lib)

ll.setPosixFilePermissions(setOf(PosixFilePermission.OWNER_EXECUTE))

bin.deleteIfExists()

bin.createSymbolicLinkPointingTo(ll)
