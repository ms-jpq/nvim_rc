local vim_home = vim.env["XDG_CONFIG_HOME"] .. "/nvim"
local py_main = vim_home .. "/init.py"


local on_stderr = function (err, msg)
  vim.api.nvim_err_write(table.concat(msg, "\n") .. "\n")
end

local chan = vim.fn.jobstart({py_main}, { rpc = true, on_stderr = on_stderr })


lv = {}
lv.notify = function (event, args)
  vim.rpcnotify(chan, event, args)
end


lv.notify("EVENT", {"ARG1", "ARG2", "ARG3"})
