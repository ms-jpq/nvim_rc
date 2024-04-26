autocmd BufEnter,CursorHold,InsertLeave <buffer> lua vim.lsp.codelens.refresh()
autocmd CursorHold,CursorHoldI          <buffer> lua vim.lsp.buf.document_highlight()
autocmd CursorMoved                     <buffer> lua vim.lsp.buf.clear_references()
