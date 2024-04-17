// ; exec go run "$0" "$@"
package main

import (
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

func main() {
	version := runtime.Version()
	if version < "go1.20" {
		os.Exit(0)
	}
	lib, ok := os.LookupEnv("LIB")
	if !ok {
		log.Panic()
	}
	bin, ok := os.LookupEnv("BIN")
	if !ok {
		log.Panic()
	}
	if runtime.GOOS == "windows" {
		bin += ".exe"
	}

	name := filepath.Base(bin)
	dst := filepath.Join(lib, "bin", name)

	cmd := exec.Command("go", "install", "--", "golang.org/x/tools/gopls@latest")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Env = append(os.Environ(), "GO111MODULE=on", "GOPATH="+lib)

	if err := cmd.Run(); err != nil {
		log.Panic(err)
	}
	if err := os.RemoveAll(bin); err != nil {
		log.Panic(err)
	}
	if err := os.Symlink(dst, bin); err != nil {
		log.Panic(err)
	}
}
