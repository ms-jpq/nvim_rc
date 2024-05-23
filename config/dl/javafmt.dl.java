// ; exec java -ea -Dprogram.name="$0" "$0" "$@"

import java.lang.ProcessBuilder.Redirect;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

public class javafmt {
  public static void main(String args[]) throws Exception {
    final var self = Path.of(System.getProperty("program.name"));
    final var lib = Path.of(System.getenv("LIB"));
    final var bin = Path.of(System.getenv("BIN"));
    final var dst = lib.resolve("google-java-format.jar");
    final var repo = "google/google-java-format";

    final var p1 =
        new ProcessBuilder("env", "--", "gh-latest.sh", ".", repo)
            .redirectError(Redirect.INHERIT)
            .start();
    assert p1.waitFor() == 0;
    final var version = new String(p1.getInputStream().readAllBytes());

    final var uri =
        "https://github.com/"
            + repo
            + "/releases/latest/download/google-java-format-"
            + version.replaceFirst("^v", "")
            + "-all-deps.jar";
    final var p2 =
        new ProcessBuilder("env", "--", "get.sh", uri).redirectError(Redirect.INHERIT).start();
    assert p2.waitFor() == 0;
    final var jar = new String(p2.getInputStream().readAllBytes());

    Files.createDirectories(lib);
    Files.move(Path.of(jar), dst, StandardCopyOption.REPLACE_EXISTING);
    Files.copy(self.resolveSibling("javafmt.ex.java"), bin, StandardCopyOption.REPLACE_EXISTING);
  }
}
