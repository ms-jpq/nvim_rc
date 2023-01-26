#!/usr/bin/env -S -- dotnet fsi

open System
open System.Diagnostics
open System.IO


let tmp = Directory.CreateTempSubdirectory().FullName
let lib = Environment.GetEnvironmentVariable "LIB"
let bin = Environment.GetEnvironmentVariable "BIN"
let proxy = Path.Combine(__SOURCE_DIRECTORY__, "..", "exec", "fsautocomplete.sh")

let run arg0 (argv: 'a) =
    use proc = Process.Start(arg0, argv)

    proc.WaitForExit()
    assert (proc.ExitCode = 0)


run "dotnet" [ "tool"; "install"; "--tool-path"; tmp; "fsautocomplete" ]

do
    let uri = Environment.GetEnvironmentVariable "URI"

    let name =
        Path.Combine(Environment.CurrentDirectory, Path.GetFileNameWithoutExtension(uri))

    if Directory.Exists name then
        Directory.SetCurrentDirectory name
        run "git" [ "pull" ]
    else
        run "git" [ "clone"; "--depth"; "1"; "--"; uri; name ]


    let src = Path.Combine(name, "syntax", "fsharp.vim")

    let dst =
        Path.Combine(__SOURCE_DIRECTORY__, "..", "..", "..", "syntax", Path.GetFileName src)

    File.Delete(dst)
    File.CreateSymbolicLink(dst, src) |> ignore

try
    Directory.Delete(lib, true)
with DirectoryNotFoundException ->
    ()

File.Delete bin

Directory.Move(tmp, lib)
File.Copy(proxy, bin)
