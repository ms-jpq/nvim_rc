from logging import ERROR, WARN, Handler, LogRecord, StreamHandler, getLogger
from pathlib import Path

from pynvim.api.nvim import Nvim

log = getLogger(Path(__file__).resolve().parent.name)


def _stream_handler() -> None:
    handler = StreamHandler()
    handler.setLevel(WARN)
    log.addHandler(handler)

    def remove() -> None:
        return log.removeHandler(handler)

    return remove


remove_stream_handler = _stream_handler()


def nvim_handler(nvim: Nvim) -> Handler:
    class NvimHandler(Handler):
        def handle(self, record: LogRecord) -> None:
            msg = self.format(record)
            if record.levelno >= ERROR:
                nvim.async_call(nvim.err_write, msg)
            else:
                nvim.async_call(nvim.out_write, msg)

    return NvimHandler()
