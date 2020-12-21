local uv = vim.loop


local out_write = function (data)
  vim.schedule(function ()
    vim.api.nvim_out_write(data)
  end)
end


local err_write = function (data)
  vim.schedule(function ()
    vim.api.nvim_err_write(data)
  end)
end


local spawn = function (prog, args, cb)

  local stdin  = uv.new_pipe(false)
  local stdout = uv.new_pipe(false)
  local stderr = uv.new_pipe(false)
  local params = {stdio = {stdin, stdout, stderr},
                   args = args}

  local process, pid = nil, nil

  process, pid = uv.spawn(prog, params, function (code)
    local handles = {stdin, stdout, stderr, process}
    for _, handle in ipairs(handles) do
      uv.close(handle)
    end
    cb(code)
  end)
  assert(process, pid)

  uv.read_start(stdout, function (err, data)
    assert(not err, err)
    if data then
      out_write(data)
    end
  end)

  uv.read_start(stderr, function (err, data)
    assert(not err, err)
    if data then
      err_write(data)
    end
  end)
end


return {
  spawn = spawn
}