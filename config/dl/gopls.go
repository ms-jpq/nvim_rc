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
	lib, bin := os.Getenv("LIB"), os.Getenv("BIN")
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
		log.Fatal(err)
	}

	cmd = exec.Command("ln", "-v", "-sf", "--", dst, bin)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		log.Fatal(err)
	}
}
