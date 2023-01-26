#!/usr/bin/env -S -- dotnet fsi

open System
open System.Diagnostics
open System.IO


let tmp = Directory.CreateTempSubdirectory().FullName
let lib = Environment.GetEnvironmentVariable "LIB"
let bin = Environment.GetEnvironmentVariable "BIN"
let proxy = Path.Combine(__SOURCE_DIRECTORY__, "..", "exec", "fantomas.sh")

do
    let args = [ "tool"; "install"; "--tool-path"; tmp; "fantomas" ]
    use proc = Process.Start("dotnet", args)

    proc.WaitForExit()
    assert (proc.ExitCode = 0)

try
    Directory.Delete(lib, true)
with DirectoryNotFoundException ->
    ()

File.Delete bin

Directory.Move(tmp, lib)
File.Copy(proxy, bin)
