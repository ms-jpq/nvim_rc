from install import bash
from python.config.install import InstallSpec
from ..config.pkgs import pkg_specs
from ..config.linter import linter_specs
from ..config.fmt import fmt_specs
from ..config.lsp import lsp_specs


_install_specs = InstallSpec(pip=(),npm=(),bash=())