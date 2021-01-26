return function(args)
  local cwd = unpack(args)

  local uv = vim.loop
  local spawn = function(prog, args, input, cwd, env)
    local _env = vim.api.nvim_call_function("environ", {})
    local stdin = uv.new_pipe(false)
    local stdout = uv.new_pipe(false)
    local stderr = uv.new_pipe(false)
    local opts = {
      stdio = {stdin, stdout, stderr},
      args = args,
      cwd = cwd
    }

    local process, pid = nil, nil
    process, pid =
      uv.spawn(
      prog,
      opts,
      function(code)
        local handles = {stdin, stdout, stderr, process}
        for _, handle in ipairs(handles) do
          uv.close(handle)
        end
        vim.schedule(
          function()
            vim.api.nvim_err_writeln(" | EXITED - " .. code)
          end
        )
      end
    )
    assert(process, pid)

    uv.read_start(
      stdout,
      function(err, data)
        assert(not err, err)
        if data then
          vim.schedule(
            function()
              vim.api.nvim_out_write(data)
            end
          )
        end
      end
    )

    uv.read_start(
      stderr,
      function(err, data)
        assert(not err, err)
        if data then
          vim.schedule(
            function()
              vim.api.nvim_err_write(data)
            end
          )
        end
      end
    )

    if stdin then
      uv.write(
        stdin,
        input,
        function(err)
          assert(not err, err)
          uv.shutdown(
            stdin,
            function(err)
              assert(not err, err)
            end
          )
        end
      )
    end
  end

  local VENV = cwd .. "/.vars/runtime"
  local PATH = VENV .. "/bin:" .. vim.api.nvim_call_function("getenv", {"PATH"})
  local env = {PATH = PATH, VIRTUAL_ENV = VENV}

  local args = {
    "-m",
    "python",
    "run",
    "--socket",
    vim.api.nvim_get_vvar("servername")
  }
  spawn("python3", args, nil, cwd, env)
end
