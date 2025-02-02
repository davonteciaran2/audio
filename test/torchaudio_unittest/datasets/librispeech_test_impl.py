import os
from pathlib import Path

from torchaudio.datasets import librispeech
from torchaudio_unittest.common_utils import (
    get_whitenoise,
    normalize_wav,
    save_wav,
    TempDirMixin,
)

# Used to generate a unique transcript for each dummy audio file
_NUMBERS = ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]


def get_mock_dataset(root_dir):
    """
    root_dir: directory to the mocked dataset
    """
    mocked_data = []
    dataset_dir = os.path.join(root_dir, librispeech.FOLDER_IN_ARCHIVE, librispeech.URL)
    os.makedirs(dataset_dir, exist_ok=True)
    sample_rate = 16000  # 16kHz
    seed = 0

    for speaker_id in range(5):
        speaker_path = os.path.join(dataset_dir, str(speaker_id))
        os.makedirs(speaker_path, exist_ok=True)

        for chapter_id in range(3):
            chapter_path = os.path.join(speaker_path, str(chapter_id))
            os.makedirs(chapter_path, exist_ok=True)
            trans_content = []

            for utterance_id in range(10):
                filename = f"{speaker_id}-{chapter_id}-{utterance_id:04d}.wav"
                path = os.path.join(chapter_path, filename)

                transcript = " ".join([_NUMBERS[x] for x in [speaker_id, chapter_id, utterance_id]])
                trans_content.append(f"{speaker_id}-{chapter_id}-{utterance_id:04d} {transcript}")

                data = get_whitenoise(sample_rate=sample_rate, duration=0.01, n_channels=1, dtype="float32", seed=seed)
                save_wav(path, data, sample_rate)
                sample = (normalize_wav(data), sample_rate, transcript, speaker_id, chapter_id, utterance_id)
                mocked_data.append(sample)

                seed += 1

            trans_filename = f"{speaker_id}-{chapter_id}.trans.txt"
            trans_path = os.path.join(chapter_path, trans_filename)
            with open(trans_path, "w") as f:
                f.write("\n".join(trans_content))
    return mocked_data


class LibriSpeechTestMixin(TempDirMixin):
    backend = "default"

    root_dir = None
    samples = []

    @classmethod
    def setUpClass(cls):
        cls.root_dir = cls.get_base_temp_dir()
        cls.samples = get_mock_dataset(cls.root_dir)

    @classmethod
    def tearDownClass(cls):
        # In case of test failure
        cls.librispeech_cls._ext_audio = ".flac"

    def _test_librispeech(self, dataset):
        num_samples = 0
        for i, (data, sample_rate, transcript, speaker_id, chapter_id, utterance_id) in enumerate(dataset):
            self.assertEqual(data, self.samples[i][0], atol=5e-5, rtol=1e-8)
            assert sample_rate == self.samples[i][1]
            assert transcript == self.samples[i][2]
            assert speaker_id == self.samples[i][3]
            assert chapter_id == self.samples[i][4]
            assert utterance_id == self.samples[i][5]
            num_samples += 1

        assert num_samples == len(self.samples)
        self.librispeech_cls._ext_audio = ".flac"

    def test_librispeech_str(self):
        self.librispeech_cls._ext_audio = ".wav"
        dataset = self.librispeech_cls(self.root_dir)
        self._test_librispeech(dataset)

    def test_librispeech_path(self):
        self.librispeech_cls._ext_audio = ".wav"
        dataset = self.librispeech_cls(Path(self.root_dir))
        self._test_librispeech(dataset)
