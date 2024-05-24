// ; exec java -ea -Dprogram.name="$0" "$0" "$@"

import java.io.File;
import java.io.IOException;
import java.lang.ProcessBuilder.Redirect;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.function.Consumer;

public class gradle_ls {
  public static void main(String args[]) throws Exception {
    final var win = System.getProperty("os.name").contains("Windows");

    final var lib = Path.of(System.getenv("LIB"));
    var bin = Path.of(System.getenv("BIN"));
    if (win) {
      bin = bin.resolveSibling("gradle" + (win ? ".bat" : ""));
    }
    final var name = "gradle-language-server";
    final var tmp = Path.of(System.getenv("TMP"));
    final var dst = lib.resolve("bin").resolve(name);
    final var repo = "microsoft/vscode-gradle";

    final var p1 =
        new ProcessBuilder("env", "--", "gh-latest.sh", ".", repo)
            .redirectError(Redirect.INHERIT)
            .start();
    assert p1.waitFor() == 0;
    final var version = new String(p1.getInputStream().readAllBytes());

    final var uri = "https://github.com/" + repo + "/archive/refs/tags/" + version + ".tar.gz";
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

    final var cwd = tmp.resolve("vscode-gradle-" + version);
    final var built = cwd.resolve(name).resolve("build").resolve("install").resolve(name);
    final var p2 =
        new ProcessBuilder(cwd.resolve("gradlew") + (win ? ".bat" : ""), "installDist")
            .directory(cwd.toFile())
            .inheritIO()
            .start();
    assert p2.waitFor() == 0;

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
      Files.move(built, lib);
    }

    Files.createSymbolicLink(bin, dst);
  }
}
