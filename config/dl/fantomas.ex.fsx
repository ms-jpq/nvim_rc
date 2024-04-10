#!/usr/bin/env -S -- dotnet fsi --

open System
open System.Diagnostics
open System.IO

let bin =
    Path.Combine(__SOURCE_DIRECTORY__, "..", "lib", "fantomas.fsx", "fantomas")

let dotnet =
    AppContext.BaseDirectory
    |> Path.GetDirectoryName
    |> Path.GetDirectoryName
    |> Path.GetDirectoryName
    |> Path.GetDirectoryName

let argv = Environment.GetCommandLineArgs() |> Seq.skip 1

let _ =
    Environment.SetEnvironmentVariable("DOTNET_ROOT", dotnet)
    use proc = Process.Start(bin, argv)
    proc.WaitForExit()
    Environment.ExitCode <- proc.ExitCode
