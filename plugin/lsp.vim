augroup GoLSP
  autocmd BufEnter,CursorHold,InsertLeave <buffer> silent! lua vim.lsp.codelens.refresh()
  autocmd CursorHold,CursorHoldI          <buffer> silent! lua vim.lsp.buf.document_highlight()
  autocmd CursorMoved                     <buffer> silent! lua vim.lsp.buf.clear_references()
augroup END
