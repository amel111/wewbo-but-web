from .otakudesu import OtakudesuExtractor
from .oploverz import OploversExtractor

class ExtractorFactory:
    _extractors = {
        "otakudesu": OtakudesuExtractor,
        "oploverz": OploversExtractor
    }

    @staticmethod
    def get_extractor(name):
        extractor_class = ExtractorFactory._extractors.get(name)
        if extractor_class:
            return extractor_class()
        return None

    @staticmethod
    def list_extractors():
        return list(ExtractorFactory._extractors.keys())
