// ; exec java -ea -Dprogram.name="$0" "$0" "$@"

import java.io.File;
import java.io.IOException;
import java.lang.ProcessBuilder.Redirect;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Arrays;
import java.util.Comparator;
import java.util.function.Consumer;

public class jdtls {
  public static void main(String args[]) {
    final var uri =
        "https://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz";
    final var lib = Paths.get(System.getenv("LIB"));
    var bin = Paths.get(System.getenv("BIN"));
    if (System.getProperty("os.name").contains("Windows")) {
      bin.resolveSibling("jdtls.bat");
    }
    final var src = lib.resolve("bin").resolve(bin.getFileName().toString());

    try {
      final var tmp = Files.createTempDirectory("");

      final var procs =
          ProcessBuilder.startPipeline(
              Arrays.asList(
                  new ProcessBuilder("get.sh", uri).redirectError(Redirect.INHERIT),
                  new ProcessBuilder("unpack.sh", tmp.toString())
                      .redirectOutput(Redirect.INHERIT)
                      .redirectError(Redirect.INHERIT)));
      for (final var proc : procs) {
        assert proc.waitFor() == 0;
      }

      Consumer<Path> cp =
          p -> {
            try {
              Files.copy(p, lib.resolve(tmp.relativize(p)), StandardCopyOption.REPLACE_EXISTING);
            } catch (IOException e) {
              e.printStackTrace();
              System.exit(1);
            }
          };

      Files.deleteIfExists(bin);
      if (Files.exists(lib)) {
        try (final var st = Files.walk(lib)) {
          st.sorted(Comparator.reverseOrder()).map(Path::toFile).forEach(File::delete);
        }
      }
      try (final var st = Files.walk(tmp)) {
        st.forEach(cp);
      }
      try (final var st = Files.walk(tmp)) {
        st.sorted(Comparator.reverseOrder()).map(Path::toFile).forEach(File::delete);
      }
      Files.createSymbolicLink(bin, src);
    } catch (Exception e) {
      e.printStackTrace();
      System.exit(1);
    }
  }
}
