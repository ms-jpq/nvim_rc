#!/usr/bin/env -S java --source 11

import java.io.IOException;
import java.lang.InterruptedException;
import java.lang.ProcessBuilder.Redirect;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;

class Main {

  public static void main(String[] args)
    throws IOException, InterruptedException {
    final var lib = Paths.get(System.getenv("LIB"));
    final var bin = Paths.get(System.getenv("BIN"));
    final var tmp = Files.createTempDirectory(null);
    final var procs = ProcessBuilder.startPipeline(
      Arrays.asList(
        new ProcessBuilder("rm", "-fr", "--", lib.toString())
          .redirectError(Redirect.INHERIT),
        new ProcessBuilder("get", "--", System.getenv("URI"))
          .redirectError(Redirect.INHERIT),
        new ProcessBuilder("unpack", "--dest", tmp.toString())
          .redirectOutput(Redirect.INHERIT)
          .redirectError(Redirect.INHERIT)
      )
    );
    for (final var proc : procs) {
      assert (proc.waitFor() == 0);
    }

    Files.move(tmp, lib);
    Files.deleteIfExists(bin);
    Files.createSymbolicLink(bin, lib.resolve("bin").resolve("jdtls"));
  }
}
