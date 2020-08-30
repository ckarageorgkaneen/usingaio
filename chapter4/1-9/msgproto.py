# Example 4-1. Message protocol: read and write
from asyncio import StreamReader, StreamWriter


async def read_msg(stream: StreamReader) -> bytes:
    # Get the first 4 bytes. This is the size prefix.
    size_bytes = await stream.readexactly(4)
    # Those 4 bytes must be converted into an integer.
    size = int.from_bytes(size_bytes, byteorder='big')
    # Now we know the payload size, so we read that off the stream.
    data = await stream.readexactly(size)
    return data


async def send_msg(stream: StreamWriter, data: bytes):
    size_bytes = len(data).to_bytes(4, byteorder='big')
    # Write is the inverse of read: first we send the length of the data,
    # encoded as 4 bytes, and thereafter the data.
    stream.writelines([size_bytes, data])
    await stream.drain()
