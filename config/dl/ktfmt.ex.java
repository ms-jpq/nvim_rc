// ; exec java -ea -Dprogram.name="$0" "$0" "$@"
import java.nio.file.Path;
import java.util.stream.Stream;

public class ktfmt {
  public static void main(String args[]) throws Exception {
    final var tabsize = Integer.parseInt(args[0]);
    final var self = Path.of(System.getProperty("program.name"));
    final var java = Path.of(System.getProperty("java.home")).resolve("bin").resolve("java");
    final var jar =
        self.getParent().getParent().resolve("lib").resolve("ktfmt.java").resolve("ktfmt.jar");
    final var argv =
        Stream.of(
                Stream.of(java.toString(), "-jar", jar.toString()),
                Stream.of(args).skip(1),
                tabsize == 4 ? Stream.of("--kotlinlang-style") : Stream.of())
            .flatMap(s -> s)
            .toArray(String[]::new);

    final var proc = new ProcessBuilder(argv).inheritIO().start();
    assert proc.waitFor() == 0;
  }
}
