// ; exec go run "$0" "$@"
package main

import (
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

func init() {
	log.SetFlags(log.Lshortfile)
}

func main() {
	version := runtime.Version()
	if version < "go1.20" {
		os.Exit(0)
	}
	lib, ok := os.LookupEnv("LIB")
	if !ok {
		log.Panicln()
	}
	bin, ok := os.LookupEnv("BIN")
	if !ok {
		log.Panicln()
	}
	if runtime.GOOS == "windows" {
		bin += ".exe"
	}

	name := filepath.Base(bin)
	dst := filepath.Join(lib, "bin", name)

	cmd := exec.Command("go", "install", "-modcacherw", "--", "golang.org/x/tools/gopls@latest")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Env = append(os.Environ(), "GOPATH="+lib)

	if err := cmd.Run(); err != nil {
		log.Panicln(err)
	}
	if err := os.RemoveAll(bin); err != nil {
		log.Panicln(err)
	}
	if err := os.Symlink(dst, bin); err != nil {
		log.Panicln(err)
	}
}
