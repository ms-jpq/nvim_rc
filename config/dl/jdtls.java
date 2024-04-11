// ; exec java -ea -Dprogram.name="$0" "$0" "$@"

import java.io.File;
import java.io.IOException;
import java.lang.ProcessBuilder.Redirect;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Comparator;
import java.util.List;
import java.util.function.Consumer;

public class jdtls {
  public static void main(String args[]) throws Exception {
    final var win = System.getProperty("os.name").contains("Windows");

    final var uri =
        "https://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz";
    final var lib = Paths.get(System.getenv("LIB"));
    var bin = Paths.get(System.getenv("BIN"));
    if (win) {
      bin.resolveSibling("jdtls.bat");
    }
    final var src = lib.resolve("bin").resolve(bin.getFileName().toString());
    final var tmp = Paths.get(System.getenv("TMP"));

    final var procs =
        ProcessBuilder.startPipeline(
            List.of(
                new ProcessBuilder("env", "--", "get.sh", uri).redirectError(Redirect.INHERIT),
                new ProcessBuilder("env", "--", "unpack.sh", tmp.toString())
                    .redirectOutput(Redirect.INHERIT)
                    .redirectError(Redirect.INHERIT)));
    for (final var proc : procs) {
      assert proc.waitFor() == 0;
    }

    Files.deleteIfExists(bin);
    if (Files.exists(lib)) {
      try (final var st = Files.walk(lib)) {
        st.sorted(Comparator.reverseOrder()).map(Path::toFile).forEach(File::delete);
      }
    }

    Consumer<Path> cp =
        p -> {
          try {
            Files.copy(p, lib.resolve(tmp.relativize(p)));
          } catch (IOException e) {
            throw new RuntimeException(e);
          }
        };
    if (win) {
      try (final var st = Files.walk(tmp)) {
        st.forEach(cp);
      }
    } else {
      Files.move(tmp, lib);
    }
    Files.createSymbolicLink(bin, src);
  }
}
