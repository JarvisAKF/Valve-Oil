"""Read a board's memory through the Klipper firmware it runs, many words at a time.

The board tools read a board's bootloader and application with Klipper's `debug_read` command, one 32-bit word per
command. Sending one command and waiting for its answer before the next made a board's read take about 50 seconds;
here BATCH commands are sent at a time. Klipper's serial link delivers commands to the board in order, and never
twice, and the board answers each command once, in the order it runs them, so the answers line up with the addresses.
A board drops answers that don't fit its transmit buffer, as with 16 commands at a time on the THR: a batch whose
answers don't all arrive within SETTLE_SECONDS, or more than were asked for, is read again. Nothing waits on the
board's acknowledgement, which a dropped answer can hold back for good. Every read the tools take is checked by hash
afterwards.
"""
from __future__ import annotations

# On a Max 4, reading 32 KiB: a USB Box took 4.1 s with 8, 3.2 s with 16, and lost answers with 64; the THR, on a
# UART, took 24.5 s with 1 (as before), 5.2 s with 8, and lost answers with 16.
BATCH = 8
# How long a batch's answers may take to arrive.
SETTLE_SECONDS = 0.5
ATTEMPTS = 5


class ReadFailed(Exception):
    pass


def read_words(reader, addresses, *, order: int = 2) -> list[int]:
    """The value `debug_read` returns for each address, in order, as an unsigned integer."""
    reactor = reader.reactor
    parser = reader.get_msgparser()
    queue = reader.get_default_command_queue()
    answers: list[int] = []
    reader.register_response(lambda params: answers.append(int(params["val"]) & 0xFFFFFFFF), "debug_result")
    values: list[int] = []
    try:
        for start in range(0, len(addresses), BATCH):
            batch = addresses[start:start + BATCH]
            commands = [parser.create_command("debug_read order=%d addr=%d" % (order, address)) for address in batch]
            for _ in range(ATTEMPTS):
                del answers[:]
                for command in commands:
                    reader.raw_send(command, 0, 0, queue)
                until = reactor.monotonic() + SETTLE_SECONDS
                while len(answers) < len(batch) and reactor.monotonic() < until:
                    reactor.pause(reactor.monotonic() + 0.002)
                if len(answers) == len(batch):
                    values.extend(answers)
                    break
                # An answer was lost or came late: let any late ones arrive before the batch is sent again.
                reactor.pause(reactor.monotonic() + SETTLE_SECONDS)
            else:
                raise ReadFailed("the board did not answer debug_read at 0x%08x" % batch[0])
    finally:
        reader.register_response(None, "debug_result")
    return values


def read_bytes(reader, start: int, end: int) -> bytes:
    """The bytes from start up to end, read as little-endian 32-bit words."""
    return b"".join(value.to_bytes(4, "little") for value in read_words(reader, list(range(start, end, 4))))
