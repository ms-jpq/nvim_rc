#!/usr/bin/env -S -- kotlinc -script
import java.lang.ProcessBuilder.Redirect
import kotlin.io.path.Path
import kotlin.io.path.createSymbolicLinkPointingTo
import kotlin.io.path.deleteIfExists

val lib = Path(System.getenv("LIB")!!)
val sh = lib.resolve("kotlin-lsp.sh")
val bin = Path(System.getenv("BIN")!!)

val uri = "https://download-cdn.jetbrains.com/kotlin-lsp/0.252.16998/kotlin-0.252.16998.zip"
val procs =
    ProcessBuilder.startPipeline(
        listOf(
            ProcessBuilder("env", "--", "get.sh", uri).redirectError(Redirect.INHERIT),
            ProcessBuilder("env", "--", "unpack.sh", lib.toString())
                .redirectOutput(Redirect.INHERIT)
                .redirectError(Redirect.INHERIT),
        )
    )

procs.forEach {
    val code = it.waitFor()
    if (code != 0) {
        System.exit(code)
    }
}

bin.deleteIfExists()

bin.createSymbolicLinkPointingTo(sh)
