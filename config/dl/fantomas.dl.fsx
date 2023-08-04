#!/usr/bin/env -S -- dotnet fsi --gui-

open System
open System.Diagnostics
open System.IO
open System.Runtime.InteropServices

let tmp = Directory.CreateTempSubdirectory().FullName
let proxy = Path.Combine(__SOURCE_DIRECTORY__, "fantomas.ex.sh")
let lib = Environment.GetEnvironmentVariable "LIB"
let bin = Environment.GetEnvironmentVariable "BIN"

let run arg0 (argv: 'a) =
    use proc = Process.Start(arg0, argv)

    proc.WaitForExit()
    assert (proc.ExitCode = 0)

run "dotnet" [ "tool"; "install"; "--tool-path"; tmp; "fantomas" ]

try
    Directory.Delete(lib, true)
with :? DirectoryNotFoundException ->
    ()

File.Delete bin
run "mv" [ "-f"; tmp; lib ]
File.Copy(proxy, bin)
