from fnmatch import fnmatch
from pathlib import Path
from shutil import which

from pynvim import Nvim
from pynvim_pp.lib import write
from std2.pickle import encode
from std2.types import never

from ..config.lsp import RootPattern, RPFallback, lsp_specs
from ..registery import atomic, keymap, rpc


@rpc(blocking=True)
def _find_root(nvim: Nvim, pattern: RootPattern, filename: str, bufnr: int) -> str:
    path = Path(filename)
    for parent in path.parents:
        for member in parent.iterdir():
            name = member.name
            if name in pattern.exact:
                return str(parent)
            else:
                for glob in pattern.glob:
                    if fnmatch(name, glob):
                        return str(parent)
    else:
        if pattern.fallback is RPFallback.cwd:
            cwd: str = nvim.funcs.getcwd()
            return cwd
        elif pattern.fallback is RPFallback.home:
            return str(Path.home())
        elif pattern.fallback is RPFallback.parent:
            return str(path.parent)
        else:
            never(pattern)


@rpc(blocking=True)
def _on_attach(nvim: Nvim, server: str) -> None:
    write(nvim, f"LSP: {server} 已加载")


_LSP_INIT = """
(function (root_fn, attach_fn, server, cfg, root_cfg)
  local lsp = require "lspconfig"
  local configs = require "lspconfig/configs"

  cfg.on_attach = function (client, bufnr)
    _G[attach_fn](server)
  end

  if root_cfg ~= vim.NIL then
    cfg.root_dir = function (filename, bufnr)
        local root = _G[root_fn](root_cfg, filename, bufnr)
        return root ~= vim.NIL and root or nil
    end
  end

  if not lsp[server] then
    configs[server] = { default_config = cfg }
  end

  lsp[server].setup(cfg)
end)(...)
"""

for spec in lsp_specs:
    if which(spec.bin):
        config = {**spec.config}
        if spec.filetypes:
            config["filetypes"] = spec.filetypes
        if spec.args:
            config["cmd"] = tuple((spec.bin, *spec.args))

        args = (
            _find_root.name,
            _on_attach.name,
            spec.server,
            encode(config),
            encode(spec.root),
        )
        atomic.exec_lua(_LSP_INIT, args)

atomic.command("doautoall Filetype")


keymap.n("H") << "<cmd>lua vim.lsp.util.show_line_diagnostics()<cr>"
keymap.n("K") << "<cmd>lua vim.lsp.buf.hover()<cr>"
keymap.n("L") << "<cmd>lua vim.lsp.buf.code_action()<cr>"
keymap.n("R") << "<cmd>lua vim.lsp.buf.rename()<cr>"

keymap.n("gp") << "<cmd>lua vim.lsp.buf.definition()<cr>"
keymap.n("gP") << "<cmd>lua vim.lsp.buf.references()<cr>"

keymap.n("gl") << "<cmd>lua vim.lsp.buf.declaration()<cr>"
keymap.n("gL") << "<cmd>lua vim.lsp.buf.implementation()<cr>"

keymap.n("go") << "<cmd>lua vim.lsp.buf.signature_help()<cr>"
keymap.n("gO") << "<cmd>lua vim.lsp.buf.type_definition()<cr>"

keymap.n("ge") << "<cmd>lua vim.lsp.buf.document_symbol()<cr>"
keymap.n("gE") << "<cmd>lua vim.lsp.buf.workspace_symbol()<cr>"

keymap.n("g[") << "<cmd>lua vim.lsp.diagnostic.goto_prev()<cr>"
keymap.n("g]") << "<cmd>lua vim.lsp.diagnostic.goto_next()<cr>"
