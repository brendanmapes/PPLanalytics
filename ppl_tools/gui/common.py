import sys
import traceback

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(tuple)
    finished = Signal()
    progress = Signal(int)

class Worker(QRunnable):
    """
    Worker thread, handling thread setup, signals, and wrap-up.
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.is_cancelled: bool = False

        # Add progress callback and cancellation check to kwargs
        self.kwargs['progress_callback'] = self.signals.progress
        self.kwargs['cancellation_check'] = self.is_cancelled_check

    @Slot()
    def run(self):
        """
        Initialize the runner function with passed args, kwargs.
        """
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            if not self.is_cancelled:
                self.signals.result.emit(result) # Return result of processing
        finally:
            self.signals.finished.emit() # Done

    def cancel(self):
        self.is_cancelled = True

    def is_cancelled_check(self):
        return self.is_cancelled
