// ; exec java -ea -Dprogram.name="$0" "$0" "$@"
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.stream.Stream;

public class ktfmt {
  public static void main(String args[]) throws Exception {
    final var self = Paths.get(System.getProperty("program.name"));
    final var jar =
        self.getParent().getParent().resolve("lib").resolve("ktfmt.java").resolve("ktfmt.jar");
    final var argv =
        Stream.concat(
                Arrays.stream(new String[] {"java", "-jar", jar.toString()}), Arrays.stream(args))
            .toArray(String[]::new);

    final var proc = new ProcessBuilder(argv).inheritIO().start();
    assert proc.waitFor() == 0;
  }
}
