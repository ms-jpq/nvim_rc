#!/usr/bin/env -S -- dotnet fsi --gui-

open System
open System.Diagnostics
open System.IO
open System.Runtime.InteropServices

let tmp = Directory.CreateTempSubdirectory().FullName
let proxy = Path.Combine(__SOURCE_DIRECTORY__, "fantomas.ex.sh")
let lib = Environment.GetEnvironmentVariable "LIB"
let bin = Environment.GetEnvironmentVariable "BIN"

do
    let args = [ "tool"; "install"; "--tool-path"; tmp; "fantomas" ]
    use proc = Process.Start("dotnet", args)

    proc.WaitForExit()
    assert (proc.ExitCode = 0)

try
    Directory.Delete(lib, true)
with :? DirectoryNotFoundException ->
    ()

File.Delete bin
Directory.Move(tmp, lib)
File.Copy(proxy, bin)
