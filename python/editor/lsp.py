from ..registery import keymap


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
