local uv = vim.loop

local spawn = function (prog, args, options)

  local stdin  = uv.new_pipe(false)
  local stdout = uv.new_pipe(false)
  local stderr = uv.new_pipe(false)
  local params = {stdio = {stdin, stdout, stderr},
                   args = args
                   env  = options.env or {}}

  local process, pid = nil, nil

  process, pid = uv.spawn(prog, params, function (code)
    local handles = {stdin, stdout, stderr, process}
    for _, handle in ipairs(handles) do
      uv.close(handle)
    end
    (options.on_exit or function () end)(code)
  end)
  assert(process, pid)

  uv.read_start(stdout, function (err, data)
    assert(not err, err)
    if data then
      vim.schedule(function ()
        (options.on_out or function () end)(data)
      end)
    end
  end)

  uv.read_start(stderr, function (err, data)
    assert(not err, err)
    if data then
      vim.schedule(function ()
        (options.on_err or function () end)(data)
      end)
    end
  end)
end


return {
  spawn = spawn
}