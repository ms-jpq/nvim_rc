#!/usr/bin/env -S -- dotnet fsi --gui-

open System
open System.Diagnostics
open System.IO
open System.Runtime.InteropServices


let py = Environment.GetEnvironmentVariable "PYTHON"
let lib = Environment.GetEnvironmentVariable "LIB"
let libexec = Environment.GetEnvironmentVariable "LIBEXEC"
let proxy = Path.Combine(__SOURCE_DIRECTORY__, "omnisharp.ex.sh")
let tmp = Directory.CreateTempSubdirectory().FullName

let base_uri =
    "https://github.com/OmniSharp/omnisharp-roslyn/releases/latest/download/omnisharp"

let uri =
    if RuntimeInformation.IsOSPlatform(OSPlatform.OSX) then
        sprintf "%s-%s" base_uri "osx-arm64-net6.0.tar.gz"
    elif RuntimeInformation.IsOSPlatform(OSPlatform.Linux) then
        sprintf "%s-%s" base_uri "linux-x64-net6.0.tar.gz"
    else
        sprintf "%s-%s" base_uri "win-x64-net6.0.zip"

let bin =
    let ext =
        if RuntimeInformation.IsOSPlatform(OSPlatform.Windows) then
            ".sh"
        else
            null

    (Environment.GetEnvironmentVariable "BIN", ext) |> Path.ChangeExtension

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

""
|> run py [ Path.Combine(libexec, "get.py"); "--"; uri ]
|> run py [ Path.Combine(libexec, "unpack.py"); "--dst"; tmp ]
|> Console.Write

File.Delete bin

try
    Directory.Delete(lib, true)
with :? DirectoryNotFoundException ->
    ()

"" |> run "mv" [ "-v"; "-f"; tmp; lib ] |> Console.Write
File.Copy(proxy, bin)
