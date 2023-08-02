#!/usr/bin/env -S -- kotlinc -script
import java.lang.ProcessBuilder.Redirect
import java.net.URI
import javax.xml.parsers.DocumentBuilderFactory
import javax.xml.xpath.XPathFactory
import kotlin.io.path.Path
import kotlin.io.path.copyTo
import kotlin.io.path.createDirectory
import kotlin.io.path.deleteRecursively

val root = URI("https://repo1.maven.org/maven2/com/facebook/ktfmt/")
val proxy = Path("", "..", "..", "config", "dl", "ktfmt.ex.sh")
val lib = Path(System.getenv("LIB")!!)
val bin = Path(System.getenv("BIN")!!)

val version =
    XPathFactory.newInstance()
        .newXPath()
        .evaluate(
            "/metadata/versioning/versions/version[last()]",
            DocumentBuilderFactory.newInstance()
                .newDocumentBuilder()
                .parse(root.resolve("maven-metadata.xml").toString()))

val jar = root.resolve("$version/ktfmt-$version-jar-with-dependencies.jar").toString()
val proc = ProcessBuilder("get.py", "--", jar).redirectError(Redirect.INHERIT).start()

assert(proc.waitFor() == 0)

val file = Path(String(proc.getInputStream().readAllBytes()))

@OptIn(kotlin.io.path.ExperimentalPathApi::class) lib.deleteRecursively()

lib.createDirectory()

file.copyTo(lib.resolve(file.getFileName()))

proxy.copyTo(bin, true)
