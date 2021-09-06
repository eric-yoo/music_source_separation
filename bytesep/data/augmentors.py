from typing import Dict

import librosa
import numpy as np

from bytesep.utils import (
    db_to_magnitude,
    get_pitch_shift_factor,
    magnitude_to_db,
)

'''
class Augmentor:
    def __init__(self, augmentation: Dict, random_seed=1234):
        r"""Augmentor for augment a waveform.

        Args:
            augmentation: Dict, e.g, {
                'pitch_shift': 4,
                'magnitude_scale': {'lower_db': -20, 'higher_db': 20}
                ...,
            }
            random_seed: int
        """
        self.augmentation = augmentation
        self.random_state = np.random.RandomState(random_seed)

    def __call__(self, waveform: np.array) -> np.array:
        r"""Augment a waveform.

        Args:
            waveform: (channels_num, audio_samples)

        Returns:
            new_waveform: (channels_num, new_audio_samples)
        """
        if 'pitch_shift' in self.augmentation.keys():
            waveform = self.pitch_shift(waveform)

        if 'magnitude_scale' in self.augmentation.keys():
            waveform = self.magnitude_scale(waveform)

        # from IPython import embed; embed(using=False); os._exit(0)

        return waveform

    def pitch_shift(self, waveform: np.array) -> np.array:
        r"""Shift pitch of a waveform. The length of the returned waveform will
        be changed.

        Args:
            waveform: (channels_num, audio_samples)

        Returns:
            new_waveform: (channels_num, new_audio_samples)
        """

        # maximum pitch shift in semitones
        max_pitch_shift = self.augmentation['pitch_shift']

        if max_pitch_shift == 0:  # No pitch shift augmentation.
            return waveform

        # random pitch shift
        rand_pitch = self.random_state.uniform(
            low=-max_pitch_shift, high=max_pitch_shift
        )

        # Pitch shift factor indicates how much a signal is stretched or
        # squeezed along the time axis.
        pitch_shift_factor = get_pitch_shift_factor(rand_pitch)
        dummy_sample_rate = 10000  # Dummy constant.

        channels_num = waveform.shape[0]

        if channels_num == 1:
            waveform = np.squeeze(waveform)

        new_waveform = librosa.resample(
            y=waveform,
            orig_sr=dummy_sample_rate,
            target_sr=dummy_sample_rate / pitch_shift_factor,
            res_type='linear',
            axis=-1,
        )

        if channels_num == 1:
            new_waveform = new_waveform[None, :]

        return new_waveform

    def magnitude_scale(self, waveform: np.array) -> np.array:
        r"""Scale the magnitude of a waveform.

        Args:
            waveform: (channels_num, audio_samples)

        Returns:
            new_waveform: (channels_num, audio_samples)
        """
        lower_db = self.augmentation['magnitude_scale']['lower_db']
        higher_db = self.augmentation['magnitude_scale']['higher_db']

        if lower_db == 0 and higher_db == 0:  # No magnitude scale augmentation.
            return waveform

        # The magnitude (in dB) of the sample with the maximum value.
        waveform_db = magnitude_to_db(np.max(np.abs(waveform)))

        new_waveform_db = self.random_state.uniform(
            waveform_db + lower_db, min(waveform_db + higher_db, 0)
        )

        relative_db = new_waveform_db - waveform_db

        relative_scale = db_to_magnitude(relative_db)

        new_waveform = waveform * relative_scale

        return new_waveform
'''

class Augmentor:
    def __init__(self, augmentations: Dict, random_seed=1234):
        r"""Augmentor for augment a waveform.

        Args:
            augmentations: Dict, e.g, {
                'pitch_shift': {'vocals': 4, 'accompaniment': 2},
                'magnitude_scale': {
                    'vocals': {'lower_db': -20, 'higher_db': 20},
                    'accompaniment': {'lower_db': -20, 'higher_db': 20}
                }
                ...,
            }
            random_seed: int
        """
        self.augmentations = augmentations
        self.random_state = np.random.RandomState(random_seed)

    def __call__(self, waveform: np.array, source_type: str) -> np.array:
        r"""Augment a waveform.

        Args:
            waveform: (channels_num, audio_samples)

        Returns:
            new_waveform: (channels_num, new_audio_samples)
        """
        if 'pitch_shift' in self.augmentations.keys():
            waveform = self.pitch_shift(waveform, source_type)

        if 'magnitude_scale' in self.augmentations.keys():
            waveform = self.magnitude_scale(waveform, source_type)

        return waveform

    def pitch_shift(self, waveform: np.array, source_type: str) -> np.array:
        r"""Shift pitch of a waveform. The length of the returned waveform will
        be changed.

        Args:
            waveform: (channels_num, audio_samples)

        Returns:
            new_waveform: (channels_num, new_audio_samples)
        """

        # maximum pitch shift in semitones
        max_pitch_shift = self.augmentations['pitch_shift'][source_type]

        if max_pitch_shift == 0:  # No pitch shift augmentations.
            return waveform

        # random pitch shift
        rand_pitch = self.random_state.uniform(
            low=-max_pitch_shift, high=max_pitch_shift
        )

        # Pitch shift factor indicates how much a signal is stretched or
        # squeezed along the time axis. We use librosa.resample instead of 
        # librosa.effects.pitch_shift because it is 10x times faster.
        pitch_shift_factor = get_pitch_shift_factor(rand_pitch)
        dummy_sample_rate = 10000  # Dummy constant.

        channels_num = waveform.shape[0]

        if channels_num == 1:
            waveform = np.squeeze(waveform)

        new_waveform = librosa.resample(
            y=waveform,
            orig_sr=dummy_sample_rate,
            target_sr=dummy_sample_rate / pitch_shift_factor,
            res_type='linear',
            axis=-1,
        )

        if channels_num == 1:
            new_waveform = new_waveform[None, :]

        return new_waveform

    def magnitude_scale(self, waveform: np.array, source_type: str) -> np.array:
        r"""Scale the magnitude of a waveform.

        Args:
            waveform: (channels_num, audio_samples)

        Returns:
            new_waveform: (channels_num, audio_samples)
        """
        lower_db = self.augmentations['magnitude_scale'][source_type]['lower_db']
        higher_db = self.augmentations['magnitude_scale'][source_type]['higher_db']

        if lower_db == 0 and higher_db == 0:  # No magnitude scale augmentation.
            return waveform

        # The magnitude (in dB) of the sample with the maximum value.
        waveform_db = magnitude_to_db(np.max(np.abs(waveform)))

        new_waveform_db = self.random_state.uniform(
            waveform_db + lower_db, min(waveform_db + higher_db, 0)
        )

        relative_db = new_waveform_db - waveform_db

        relative_scale = db_to_magnitude(relative_db)

        new_waveform = waveform * relative_scale

        return new_waveform