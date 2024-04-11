// ; exec java -ea -Dprogram.name="$0" "$0" "$@"
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.stream.Stream;

public class javafmt {
  public static void main(String args[]) throws Exception {
    final var self = Paths.get(System.getProperty("program.name"));
    final var java = Paths.get(System.getProperty("java.home")).resolve("bin").resolve("java");
    final var jar =
        self.getParent()
            .getParent()
            .resolve("lib")
            .resolve("javafmt.java")
            .resolve("google-java-format.jar");
    final var argv =
        Stream.concat(Stream.of(java.toString(), "-jar", jar.toString()), Arrays.stream(args))
            .toArray(String[]::new);

    final var proc = new ProcessBuilder(argv).inheritIO().start();
    assert proc.waitFor() == 0;
  }
}
