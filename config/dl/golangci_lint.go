// ; exec go run "$0" "$@"
package main

import (
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
)

func init() {
	log.SetFlags(log.Lshortfile)
}

const repo = "golangci/golangci-lint"

func main() {
	base := fmt.Sprintf("https://github.com/%s/releases/latest/download/golangci-lint", repo)

	bin, ok := os.LookupEnv("BIN")
	if !ok {
		log.Panicln()
	}
	ext := "tar.gz"
	if runtime.GOOS == "windows" {
		bin += ".exe"
		ext = "zip"
	}

	tmp, ok := os.LookupEnv("TMP")
	if !ok {
		log.Panicln()
	}

	cmd := exec.Command("env", "--", "gh-latest.sh", ".", repo)
	cmd.Stderr = os.Stderr
	output, err := cmd.Output()
	if err != nil {
		log.Panicln(err)
	}
	version, _ := strings.CutPrefix(string(output), "v")

	uri := fmt.Sprintf("%s-%s-%s-%s.%s", base, version, runtime.GOOS, runtime.GOARCH, ext)

	get := exec.Command("env", "--", "get.sh", uri)
	unpack := exec.Command("env", "--", "unpack.sh", tmp)
	get.Stderr = os.Stderr
	unpack.Stderr = os.Stderr
	r, w := io.Pipe()
	get.Stdout = w
	unpack.Stdin = r

	wg := sync.WaitGroup{}

	go func() {
		defer wg.Done()
		defer w.Close()
		if err := get.Run(); err != nil {
			log.Panicln(err)
		}
	}()
	go func() {
		defer wg.Done()
		if err := unpack.Run(); err != nil {
			log.Panicln(err)
		}
	}()
	wg.Add(2)
	wg.Wait()

	pat := filepath.Join(tmp, "*", "golangci-lint*")
	globbed, err := filepath.Glob(pat)
	if err != nil {
		log.Panicln(err)
	}
	if err = os.Rename(globbed[0], bin); err != nil {
		log.Panicln(err)
	}
}
