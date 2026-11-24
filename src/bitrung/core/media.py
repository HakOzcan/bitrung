"""
@file media.py
@brief What a source file holds, as ffprobe reports it.
"""

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

## @brief Subtitle codecs we can turn into WebVTT.
## @details The others, like PGS and DVD subtitles, are pictures.
TEXT_SUBTITLES = frozenset({"subrip", "ass", "ssa", "mov_text", "webvtt"})


class Transfer(StrEnum):
    """@brief How brightness is stored: SDR, or one of two HDR curves."""

    SDR = "sdr"
    PQ = "pq"  # SMPTE ST 2084: HDR10, HDR10+ and Dolby Vision
    HLG = "hlg"  # ARIB STD-B67: mostly TV broadcasts


@dataclass(frozen=True, slots=True)
class MasteringDisplay:
    """
    @brief The screen the film was graded on (HDR10 static metadata).
    @details Colors are CIE 1931 (x, y) points, luminance is in cd/m2.
    """

    red: tuple[Fraction, Fraction]
    green: tuple[Fraction, Fraction]
    blue: tuple[Fraction, Fraction]
    white_point: tuple[Fraction, Fraction]
    min_luminance: Fraction
    max_luminance: Fraction


@dataclass(frozen=True, slots=True)
class ContentLight:
    """
    @brief How bright the film gets (HDR10 static metadata).
    @details max_cll is the brightest pixel and max_fall the brightest
             frame average, both in cd/m2. 0 means the file doesn't say.
    """

    max_cll: int
    max_fall: int


@dataclass(frozen=True, slots=True)
class DolbyVision:
    """
    @brief The Dolby Vision record of a stream.
    @details compatibility says what players without Dolby Vision get
             from the base layer: 0 nothing usable, 1 HDR10, 2 SDR,
             4 HLG, 6 Blu-ray HDR10.
    """

    profile: int
    level: int
    compatibility: int


@dataclass(frozen=True, slots=True)
class VideoStream:
    """@brief The main picture of a file, with its HDR metadata."""

    index: int
    codec: str
    width: int
    height: int
    sar: Fraction  # the shape of one pixel, 1 = square
    frame_rate: Fraction | None
    transfer: Transfer
    mastering: MasteringDisplay | None = None
    content_light: ContentLight | None = None
    dolby_vision: DolbyVision | None = None
    hdr10plus: bool = False


@dataclass(frozen=True, slots=True)
class AudioStream:
    """@brief One audio track."""

    index: int
    codec: str
    profile: str | None
    channels: int
    layout: str | None
    language: str
    title: str | None
    default: bool


@dataclass(frozen=True, slots=True)
class SubtitleStream:
    """@brief One subtitle track, as text or as pictures."""

    index: int
    codec: str
    language: str
    title: str | None
    default: bool
    forced: bool
    hearing_impaired: bool

    @property
    def is_text(self) -> bool:
        """@brief True if we can turn this track into WebVTT."""
        return self.codec in TEXT_SUBTITLES


@dataclass(frozen=True, slots=True)
class MediaInfo:
    """
    @brief What one source file holds.
    @details video is None when the file has no picture, like a song
             with cover art.
    """

    duration: float  # seconds
    video: VideoStream | None
    audio: tuple[AudioStream, ...]
    subtitles: tuple[SubtitleStream, ...]
