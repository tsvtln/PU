import hashlib

class CheckSumCalculator:
    @staticmethod
    def calculate_checksum(file_path, checksum_type):
        """
        Calculate the checksum of a file using the specified type (e.g., 'sha256', 'sha1', 'md5').
        Returns the hex digest string.
        """
        hash_func = getattr(hashlib, checksum_type, None)
        if hash_func is None:
            raise ValueError(f"Unsupported checksum type: {checksum_type}")
        h = hash_func()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()