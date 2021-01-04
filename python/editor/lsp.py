from fnmatch import fnmatch
from pathlib import Path
from string import Template

from pynvim import Nvim
from std2.pickle import encode

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
        if pattern.fallback == RPFallback.cwd:
            cwd: str = nvim.funcs.getcwd()
            return cwd
        elif pattern.fallback == RPFallback.home:
            return str(Path.home())
        elif pattern.fallback == RPFallback.parent:
            return str(path.parent)
        else:
            assert False


_LSP_INIT = """
local lsp = require "lspconfig"

local root_dir = function (root_cfg)
  return function (filename, bufnr)
    return ${FIND_ROOT}(root_cfg, filename, bufnr)
  end
end

local setup = function (cfg, root_cfg)
  if root_cfg then
    cfg.root_dir = root_dir(root_cfg)
  end
  lsp.${SERVER}.setup(cfg)
end

setup(...)
"""
_TEMPLATE = Template(_LSP_INIT)

for spec in lsp_specs:
    lua = _TEMPLATE.substitute(SERVER=spec.server, FIND_ROOT=_find_root.remote_name)
    atomic.exec_lua(lua, (spec.config, encode(spec.root)))


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
