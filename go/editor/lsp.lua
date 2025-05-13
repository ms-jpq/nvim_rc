(function(ns, root_fn, attach_fn, server, cfg, root_cfg)
  local _, err =
    pcall(
    function()
      cfg.on_attach = function(client, bufnr)
        _G[ns][attach_fn](server)
      end

      if root_cfg ~= vim.NIL then
        cfg.root_dir = function(filename, bufnr)
          local root = _G[ns][root_fn](root_cfg, filename, bufnr)
          return root ~= vim.NIL and root or nil
        end
      end

      if coq ~= nil then
        cfg = coq.lsp_ensure_capabilities(cfg)
      end
      if chad ~= nil then
        cfg = chad.lsp_ensure_capabilities(cfg)
      end

      vim.lsp.config(server, cfg)
    end
  )
  if err then
    vim.api.nvim_err_writeln(err)
  end
end)(...)
