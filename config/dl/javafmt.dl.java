// ; exec java -Dprogram.name="$0" "$0" "$@"
import java.lang.ProcessBuilder.Redirect;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

public class javafmt {
  public static void main(String args[]) {
    final var self = Paths.get(System.getProperty("program.name"));
    final var lib = Paths.get(System.getenv("LIB"));
    final var bin = Paths.get(System.getenv("BIN"));
    final var dst = lib.resolve("google-java-format.jar");
    final var repo = "google/google-java-format";

    try {
      final var p1 =
          new ProcessBuilder("gh-latest.sh", ".", repo).redirectError(Redirect.INHERIT).start();
      final var c1 = p1.waitFor();
      if (c1 != 0) {
        System.exit(c1);
      }

      final var version = new String(p1.getInputStream().readAllBytes());
      final var uri =
          "https://github.com/"
              + repo
              + "/releases/latest/download/google-java-format-"
              + version.replaceFirst("^v", "")
              + "-all-deps.jar";

      final var p2 = new ProcessBuilder("get.sh", uri).redirectError(Redirect.INHERIT).start();
      final var c2 = p2.waitFor();
      if (c2 != 0) {
        System.exit(c1);
      }

      final var jar = new String(p2.getInputStream().readAllBytes());

      Files.createDirectories(lib);
      Files.copy(Paths.get(jar), dst, StandardCopyOption.REPLACE_EXISTING);
      Files.copy(self.resolveSibling("javafmt.ex.java"), bin, StandardCopyOption.REPLACE_EXISTING);
    } catch (Exception e) {
      e.printStackTrace();
      System.exit(1);
    }
  }
}
