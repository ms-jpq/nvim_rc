#!/usr/bin/env -S -- dotnet fsi --

open System
open System.Diagnostics
open System.IO
open System.Runtime.InteropServices

let tmp = Environment.GetEnvironmentVariable "TMP"
let lib = Environment.GetEnvironmentVariable "LIB"
let proxy = Path.Combine(__SOURCE_DIRECTORY__, "fsautocomplete.ex.sh")
let uri = "https://github.com/ionide/Ionide-vim"

let bin =
    let ext =
        if RuntimeInformation.IsOSPlatform(OSPlatform.Windows) then
            Path.GetExtension proxy
        else
            null

    (Environment.GetEnvironmentVariable "BIN", ext) |> Path.ChangeExtension

let run arg0 (argv: 'a) =
    use proc = Process.Start(arg0, argv)

    proc.WaitForExit()
    assert (proc.ExitCode = 0)

run "dotnet" [ "tool"; "install"; "--tool-path"; tmp; "fsautocomplete" ]

let name =
    Path.Combine(Environment.CurrentDirectory, Path.GetFileNameWithoutExtension(uri))

if Directory.Exists name then
    Directory.SetCurrentDirectory name
    run "git" [ "pull"; "--force" ]
else
    run "git" [ "clone"; "--depth"; "1"; "--"; uri; name ]

let src = Path.Combine(name, "syntax", "fsharp.vim")

let dst =
    Path.Combine(__SOURCE_DIRECTORY__, "..", "..", "syntax", Path.GetFileName src)

File.Delete(dst)
File.CreateSymbolicLink(dst, src) |> ignore

try
    Directory.Delete(lib, true)
with :? DirectoryNotFoundException ->
    ()

File.Delete bin
run "mv" [ "-f"; tmp; lib ]
File.Copy(proxy, bin)
