// ; exec java -ea -Dprogram.name="$0" "$0" "$@"

import java.io.File;
import java.lang.ProcessBuilder.Redirect;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Comparator;

public class jdtls {
  public static void main(String args[]) throws Exception {
    final var uri =
        "https://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz";
    final var lib = Paths.get(System.getenv("LIB"));
    var bin = Paths.get(System.getenv("BIN"));
    if (System.getProperty("os.name").contains("Windows")) {
      bin.resolveSibling("jdtls.bat");
    }
    final var src = lib.resolve("bin").resolve(bin.getFileName().toString());
    final var tmp = Paths.get(System.getenv("TMP"));

    final var p1 =
        new ProcessBuilder("env", "--", "get.sh", uri).redirectError(Redirect.INHERIT).start();
    assert p1.waitFor() == 0;
    final var dst = new String(p1.getInputStream().readAllBytes());

    final var p2 =
        new ProcessBuilder("env", "--", "unpack.sh", tmp.toString(), dst).inheritIO().start();
    assert p2.waitFor() == 0;

    Files.deleteIfExists(bin);
    if (Files.exists(lib)) {
      try (final var st = Files.walk(lib)) {
        st.sorted(Comparator.reverseOrder()).map(Path::toFile).forEach(File::delete);
      }
    }
    final var p3 =
        new ProcessBuilder("mv", "-f", "--", tmp.toString(), lib.toString()).inheritIO().start();
    assert p3.waitFor() == 0;

    Files.createSymbolicLink(bin, src);
  }
}
