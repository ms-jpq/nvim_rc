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
	cmd.Env = append(os.Environ(), "GO111MODULE=on", "GOPATH="+lib)
	err := cmd.Run()
	if err != nil {
		log.Fatal(err)
	}
	err = exec.Command("install", "-v", "-b", "--", dst, bin).Run()
	if err != nil {
		log.Fatal(err)
	}
}
