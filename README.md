# Pure Python Neovim Configuration

My goal is to eventually bring neovim to VScode level of experience.

I cannot do this in lua, it is too painful to use for this type of work.

## Disclaimer

All of my stuff here are private, including the dependencies.

If you want to use my config, please fork it.

### Configuration DSL

This is all type checked!

```python
settings["updatetime"] = 300
settings["whichwrap"] += ("h", "l", "<", ">", "[", "]")

keymap.nv("/", silent=False) << "/\V"
keymap.nv("?", silent=False) << "?\V"

autocmd("FocusLost", "VimLeavePre", modifiers=("*", "nested")) << "silent! wa"
```

### Typed Config

Runtime validation of configuration. You can't make typos, or type errors!

```yaml
- bin: mypy
  type: fs
  args:
    - --
    - "%"
  filetypes:
    - python
  install:
    pip:
      - mypy
```

```yaml
- uri: https://github.com/junegunn/fzf.vim
  vals:
    fzf_buffers_jump: True
    fzf_layout:
      window:
        width: 0.9
        height: 0.9
  keys:
    - modes: n
      opts:
        silent: False
      maps:
        "<leader>O": ":Rg "
```

### Multiple Package Management

Will install NPM & PIP & git packages for you in their **private** namespace.

Only accessible from inside `neovim`, under `.vars`.

```sh
init.py --install-packages
```

Will also remind you to update weekly. Runs inside `neovim` in a floating window.

### Clean Runtime Dependencies

Will also install runtime dependencies under their **private** namespace.

The runtime is isolated from your other packages!

```sh
init.py --install-runtime
```

### Extensive Built-ins

And many setting changes akin to `emacs`' `CUA` mode.

#### Linters and Prettiers

* Not only install dependencies for you

* Runs multiple linters in parallel on the same file.

* Runs multiple prettiers in sequence on the same file

#### Text Objects and Operators

* A `word` text object that works for lisps and in help docs.

* Locale aware!

* and some more basic ones like `move`, `replace`, `search`, `entire`

#### Misc

* Built-in float term

* Built-in tab detection

* Debounced auto save

* ...