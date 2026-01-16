from .otakudesu import OtakudesuExtractor

class ExtractorFactory:
    _extractors = {
        "otakudesu": OtakudesuExtractor
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
