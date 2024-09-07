import asyncio
import os
import logging
from asyncio import AbstractEventLoop

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from services.import_data import import_data_to_staging


class WatcherHandler(FileSystemEventHandler):
    def __init__(self, loop):
        self.loop = loop  # Reference to the running event loop

    def on_created(self, event) -> None:
        # Check if it's a file and not a directory
        if not event.is_directory:
            # Check if the file is a flat file (CSV in this case)
            if event.src_path.endswith('.csv'):
                logging.info(f"Detected new CSV file: {os.path.basename(event.src_path)}")

                future = asyncio.run_coroutine_threadsafe(
                    import_data_to_staging(event.src_path), self.loop
                )
                # Optionally handle any potential errors
                try:
                    result = future.result()  # This can raise exceptions if the task fails
                except Exception as e:
                    logging.exception(f"Error scheduling task: {e}")

            # TODO: optional to create process to zip and backup item before deletion
            os.remove(event.src_path)


async def watch_folder(
        loop: AbstractEventLoop,
        target_directory: str
) -> None:
    event_handler = WatcherHandler(loop)
    observer = Observer()
    observer.schedule(event_handler, target_directory, recursive=False)

    observer.start()
    logging.info(f"Watching folder: {target_directory}")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
