// ; exec -- java -Dprogram.name="$0" "$0" "$@"

import java.io.IOException;
import java.lang.ProcessBuilder.Redirect;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.StandardCopyOption;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.Arrays;

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
      while (true) {
        var dead = 0;
        for (final var proc : procs) {
          assert proc.waitFor() == 0;
          if (!proc.isAlive()) {
            dead++;
          }
        }
        if (dead == procs.size()) {
          break;
        }
        Thread.sleep(100);
      }

      Files.deleteIfExists(bin);
      if (Files.exists(lib)) {
        Files.walkFileTree(
            lib,
            new SimpleFileVisitor<Path>() {
              @Override
              public FileVisitResult visitFile(Path file, BasicFileAttributes attrs)
                  throws IOException {
                Files.delete(file);
                return FileVisitResult.CONTINUE;
              }

              @Override
              public FileVisitResult postVisitDirectory(Path dir, IOException e)
                  throws IOException {
                Files.delete(dir);
                return FileVisitResult.CONTINUE;
              }
            });
      }

      Files.move(tmp, lib, StandardCopyOption.REPLACE_EXISTING);
      Files.createSymbolicLink(bin, src);
    } catch (Exception e) {
      e.printStackTrace();
      System.exit(1);
    }
  }
}
