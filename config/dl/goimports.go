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

	dir := filepath.Join(lib, "..", "..")
	name := filepath.Base(bin)
	dst := filepath.Join(lib, "bin", name)
	sbin := filepath.Join(dir, "..", "bin", name)

	links := map[string]string{
		bin:  dst,
		sbin: dst,
	}

	cmd := exec.Command("go", "install", "-modcacherw", "--", "golang.org/x/tools/cmd/goimports@latest")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Env = append(os.Environ(), "GOPATH="+lib)

	if err := cmd.Run(); err != nil {
		log.Panicln(err)
	}
	for next, prev := range links {
		if err := os.RemoveAll(next); err != nil {
			log.Panicln(err)
		}
		if err := os.Symlink(prev, next); err != nil {
			log.Panicln(err)
		}
	}
}
