(function(ns, root_fn, attach_fn, server, cfg, root_cfg)
  local _, err =
    pcall(
    function()
      local lsp = require "lspconfig"
      local configs = require "lspconfig/configs"

      cfg.on_attach = function(client, bufnr)
        _G[ns][attach_fn](server)
      end

      local go = lsp[server] ~= nil

      if not go then
        configs[server] = {default_config = cfg}
      end

      if root_cfg ~= vim.NIL or not go then
        cfg.root_dir = function(filename, bufnr)
          local root = _G[ns][root_fn](root_cfg, filename, bufnr)
          return root ~= vim.NIL and root or nil
        end
      end

      cfg = coq.lsp_ensure_capabilities(cfg)
      cfg = chad.lsp_ensure_capabilities(cfg)

      lsp[server].setup(cfg)
    end
  )
  if err then
    vim.api.nvim_err_writeln(err)
  end
end)(...)
