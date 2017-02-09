from pythonutils.decorators import retry, NoTriesRemaining
from functools import partial
import unittest
import mock


class TestRetry(unittest.TestCase):
    def setUp(self):
        self.wrapped_fn = mock.MagicMock(return_value=1)
        self.wrapped_fn.__name__ = 'test'

    def test_no_retry(self):
        decorated = retry(retryable_vals=[None])(self.wrapped_fn)

        result = decorated(1, 2)

        self.assertIsNone(self.wrapped_fn.assert_called_with(1, 2))
        self.assertEqual(self.wrapped_fn.return_value, result)

    def test_retry_due_to_bad_return(self):
        max_attempts = 3
        decorated = retry(retryable_vals=[self.wrapped_fn.return_value], max_attempts=max_attempts)(self.wrapped_fn)

        self.assertRaises(NoTriesRemaining, partial(decorated, 1, 2))
        self.assertEqual(self.wrapped_fn.call_count, max_attempts)

    def test_retry_due_to_retryable_exception(self):
        max_attempts = 3
        decorated = retry(retryable_exceptions=[ValueError, IndexError], max_attempts=max_attempts)(self.wrapped_fn)

        self.wrapped_fn.side_effect = [ValueError for i in range(max_attempts)]

        self.assertRaises(ValueError, partial(decorated, 1, 2))
        self.assertEqual(self.wrapped_fn.call_count, max_attempts)

    def test_retry_due_to_retryable_exception_and_recovers(self):
        max_attempts = 3
        decorated = retry(retryable_exceptions=[ValueError, IndexError], max_attempts=max_attempts)(self.wrapped_fn)

        self.wrapped_fn.side_effect = [ValueError for i in range(max_attempts - 1)] + [self.wrapped_fn.return_value]

        result = decorated(1, 2)

        self.assertEqual(result, self.wrapped_fn.return_value)
        self.assertEqual(self.wrapped_fn.call_count, max_attempts)

    def test_raises_non_retryable_exceptions(self):
        max_attempts = 3
        decorated = retry(retryable_exceptions=[ValueError, IndexError], max_attempts=max_attempts)(self.wrapped_fn)

        self.wrapped_fn.side_effect = [NameError for i in range(max_attempts)]

        self.assertRaises(NameError, partial(decorated, 1, 2))
        self.assertEqual(self.wrapped_fn.call_count, 1)