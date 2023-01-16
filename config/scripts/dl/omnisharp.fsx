#!/usr/bin/env -S dotnet fsi

open System
open System.Diagnostics
open System.IO
open System.Runtime.InteropServices


let run arg0 argv (input: 'a) =
    let start =
        new ProcessStartInfo(FileName = arg0, RedirectStandardInput = true, RedirectStandardOutput = true)

    argv |> Seq.iter start.ArgumentList.Add

    use proc = Process.Start(start)

    do
        use stdin = proc.StandardInput
        stdin.Write input

    proc.WaitForExit()
    assert (proc.ExitCode = 0)
    proc.StandardOutput.ReadToEnd()


let tmp = Directory.CreateTempSubdirectory().FullName
let lib = Environment.GetEnvironmentVariable "LIB"
let bin = Environment.GetEnvironmentVariable "BIN"
let proxy = Path.Combine(__SOURCE_DIRECTORY__, "..", "exec", "omnisharp.sh")

let uri =
    let env =
        if RuntimeInformation.IsOSPlatform(OSPlatform.OSX) then
            "DARWIN_URI"
        elif RuntimeInformation.IsOSPlatform(OSPlatform.Linux) then
            "LINUX_URI"
        else
            "NT_URI"

    env |> Environment.GetEnvironmentVariable


"" |> run "get" [ "--"; uri ] |> run "unpack" [ "--dest"; tmp ] |> Console.Write

try
    Directory.Delete(lib, true)
with DirectoryNotFoundException ->
    ()

File.Delete bin

Directory.Move(tmp, lib)
File.Copy(proxy, bin)
