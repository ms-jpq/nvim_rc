#!/usr/bin/env -S -- dotnet fsi --gui-

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
let proxy = Path.Combine(__SOURCE_DIRECTORY__, "omnisharp.ex.sh")

let bin =
    let ext =
        if RuntimeInformation.IsOSPlatform(OSPlatform.Windows) then
            ".sh"
        else
            null

    (Environment.GetEnvironmentVariable "BIN", ext) |> Path.ChangeExtension

let uri =
    if RuntimeInformation.IsOSPlatform(OSPlatform.OSX) then
        "https://github.com/OmniSharp/omnisharp-roslyn/releases/latest/download/omnisharp-osx-arm64-net6.0.tar.gz"
    elif RuntimeInformation.IsOSPlatform(OSPlatform.Linux) then
        "https://github.com/OmniSharp/omnisharp-roslyn/releases/latest/download/omnisharp-linux-x64-net6.0.tar.gz"
    else
        "https://github.com/OmniSharp/omnisharp-roslyn/releases/latest/download/omnisharp-win-x64-net6.0.zip"

""
|> run "get.py" [ "--"; uri ]
|> run "unpack.py" [ "--dst"; tmp ]
|> Console.Write

try
    Directory.Delete(lib, true)
with :? DirectoryNotFoundException ->
    ()

File.Delete bin
Directory.Move(tmp, lib)
File.Copy(proxy, bin)
