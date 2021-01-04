# Pure Python Neovim Configuration

Author of [CHADTree](https://github.com/ms-jpq/chadtree) here.

My goal is to eventually bring neovim to VSCode level of experience.

I cannot do this in lua, it is too painful to use for this type of work.

## Disclaimer

All of my stuff here are private, including the dependencies.

If you want to use my config, please fork it, because I will tinker with stuff all the time.

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

Only accessible from inside `neovim`.

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

- Not only install dependencies for you

- Able to run multiple linters in parallel on the same file

- Able to run multiple prettiers in sequence on the same file

#### Text Objects and Operators

- A `word` text object that works for lisps and in help docs

- Locale aware!

- and some more basic ones like `move`, `replace`, `search`, `entire`

#### Misc

- Built-in float term

- Built-in tab detection

- Debounced auto save

- ...

### Comparion between Vim style thinking and a saner approach with a saner language

Prefix: I am not ragging on any of the other plugin authors. In fact I use alot of the plugins written in a VimL style. However, I do think the old way of doing things is a bit insane, as you will see in my comparison.

Due to the well known limitations of VimL there is this tendency for things written in VimL to use alot of built-in functions, especially regex, which is in my opinion is counter productive because they introduce much accidental complexity.

Take the example of `tab detection`.

We have two essential problems:

1. Should I use tab or space for this file?

2. What is the predominate tab size?

#### VimL Style

Look at how a popular Vim plugin [solves this](https://github.com/tpope/vim-sleuth/blob/master/plugin/sleuth.vim):

From a glance we can know that:

- It is language specific

- It tries to detect comments

- It has some fairly "intricate" regex beyond just "tell me where whitespaces are"

Now something like this is not only very difficult to read, but also even harder to generalize onto all filetypes, and ensure there are no werid corner cases.

#### Sane Style

Now compare this to the following naive algorithm

1. Sample some lines from the file deterministically

2. If the lines start with more tabs than spaces, indent with `tabs`, else with `spaces`

3. For each line in sample, from `i` in `[2..8]`, expand tabs with `i` spaces

4. Calculate `indent_level` for each line in step #3 and `divisibility` of `indent_level / i` if `indent_level > 0`

5. Reverse sort by `divisibility, i` in lexicographic order, the foremost `i` is the indent level

Now this is not only easy to implement, it is also very easy to understand.

We only do `[2..8]` because no sane person would use `> 8` levels of indent.

The indent level with the greatest `divisibility` implies that most lines are indented at that level.

To solve the issue of common divisors, we sort by highest `i`
